"""Pantallas complementarias de Job to go (Streamlit, sin nuevo modelo de nodos)."""
from datetime import date, timedelta
import streamlit as st
from jobtogo_ui import (hero as ui_hero, section as ui_section, job_card,
                       portrait_card, safe, format_cop, notice)
from jobtogo_mejoras import (
    ofertas_detalladas, favoritos, guardar_favorito, quitar_favorito,
    postulaciones_con_estado, postular_vacante,
    empresas_disponibles, mis_solicitudes_laborales,
    solicitar_vinculacion, solicitar_desvinculacion,
    solicitudes_laborales_empresa, resolver_solicitud_laboral,
    postulantes_empresa, cambiar_estado_postulacion,
    cambiar_estado_vacante, notificaciones, marcar_notificaciones_leidas,
    ESTADOS_POSTULACION,
)


def encabezado(kicker, titulo, texto):
    ui_hero(kicker, titulo, texto)


def accion(func, *args, mensaje='Cambio guardado correctamente.'):
    try:
        func(*args)
        st.session_state['jtg_mensaje'] = mensaje
        st.rerun()
    except Exception as exc:
        st.error(f'No fue posible completar la operación: {exc}')


def mensaje_pendiente():
    mensaje = st.session_state.pop('jtg_mensaje', None)
    if mensaje:
        st.success(mensaje)


def pagina_busqueda(usuario_id):
    encabezado('Oportunidades', 'Encuentra tu próximo empleo',
               'Explora vacantes, filtra por tus intereses y postúlate desde tu perfil.')
    mensaje_pendiente()
    todas = ofertas_detalladas(usuario_id)
    postulados = {r['id'] for r in postulaciones_con_estado(usuario_id)}
    if not todas:
        st.info('Todavía no hay ofertas publicadas.')
        return
    filtros, resultados = st.columns([1.05, 2.45], gap='large')
    with filtros:
        with st.container(border=True):
            ui_section('Filtros', 'Personaliza los resultados')
            busqueda = st.text_input('Palabras clave', placeholder='Cargo, habilidad o empresa')
            ciudades = sorted({str(o['ubicacion']) for o in todas if o.get('ubicacion')})
            ubicaciones = st.multiselect('Ubicación', ciudades)
            empresas = sorted({str(o['empresa']) for o in todas if o.get('empresa')})
            empresa_sel = st.multiselect('Empresa', empresas)
            contratos = sorted({str(o['tipo_contrato']) for o in todas if o.get('tipo_contrato')})
            contrato_sel = st.multiselect('Tipo de contrato', contratos)
            habilidades = sorted({h for o in todas for h in (o.get('habilidades') or []) if h})
            hab_sel = st.multiselect('Habilidades requeridas', habilidades)
            salario_min = st.number_input('Salario mínimo (COP)', min_value=0, step=500000, value=0)
            solo_abiertas = st.checkbox('Solo vacantes abiertas', value=False)
    encontrados=[]
    for o in todas:
        texto = ' '.join(str(o.get(k) or '') for k in ('titulo','descripcion','empresa','ubicacion')).casefold()
        if busqueda and busqueda.casefold() not in texto: continue
        if ubicaciones and o.get('ubicacion') not in ubicaciones: continue
        if empresa_sel and o.get('empresa') not in empresa_sel: continue
        if contrato_sel and o.get('tipo_contrato') not in contrato_sel: continue
        if hab_sel and not set(hab_sel).issubset(set(o.get('habilidades') or [])): continue
        if float(o.get('salario') or 0) < salario_min: continue
        if solo_abiertas and o['estado_visible'] != 'Abierta': continue
        encontrados.append(o)
    with resultados:
        cabecera, ordenar_col = st.columns([1.15, 1], gap='small')
        with cabecera:
            ui_section('Vacantes disponibles', f'{len(encontrados)} resultado(s) de {len(todas)}')
        with ordenar_col:
            orden = st.selectbox('Ordenar por', ['Mayor compatibilidad', 'Mayor salario', 'Nombre de la oferta'])
        if orden == 'Mayor compatibilidad':
            encontrados.sort(key=lambda o:(-int(o['coincidencias']), -float(o.get('salario') or 0)))
        elif orden == 'Mayor salario':
            encontrados.sort(key=lambda o:-float(o.get('salario') or 0))
        else:
            encontrados.sort(key=lambda o:(o.get('titulo') or '').casefold())
        for o in encontrados:
            abierta = o['estado_visible'] == 'Abierta'
            with st.container(border=True):
                job_card(o, embedded=True, compact=True)
                favorito_col, postular_col, _ = st.columns([1.1, 1.2, 1.1], gap='small')
                with favorito_col:
                    if o.get('guardada'):
                        if st.button('Quitar favorito',key=f'quitar_fav_{o["id"]}',use_container_width=True):
                            accion(quitar_favorito,usuario_id,o['id'],mensaje='Vacante quitada de favoritos.')
                    else:
                        if st.button('Guardar',key=f'fav_{o["id"]}',use_container_width=True):
                            accion(guardar_favorito,usuario_id,o['id'],mensaje='Vacante guardada.')
                with postular_col:
                    if o['id'] in postulados:
                        st.caption('Postulación enviada')
                    elif st.button('Postularme', key=f'postular_nueva_{o["id"]}',
                                   disabled=not abierta, type='primary',use_container_width=True):
                        accion(postular_vacante,usuario_id,o['id'],mensaje='Postulación enviada correctamente.')
                if not abierta:
                    st.caption('Esta vacante no admite nuevas postulaciones.')
        if not encontrados:
            st.info('No encontramos vacantes con esos filtros. Prueba ampliar tu búsqueda.')


def pagina_favoritos(usuario_id):
    encabezado('Mis oportunidades', 'Empleos guardados',
               'Organiza las vacantes que te interesan y consúltalas cuando quieras.')
    mensaje_pendiente()
    datos=favoritos(usuario_id)
    if not datos:
        st.info('Todavía no has guardado vacantes. Puedes hacerlo desde Buscar empleos.')
        if st.button('Explorar vacantes', type='primary'):
            st.session_state['pagina_actual']='Buscar empleos';st.rerun()
        return
    ui_section('Tus favoritos', f'{len(datos)} vacante(s) guardada(s)')
    for r in datos:
        with st.container(border=True):
            job_card(r,embedded=True,compact=True)
            if st.button('Quitar de guardados',key=f'fav_quitar_{r["id"]}'):
                accion(quitar_favorito,usuario_id,r['id'],mensaje='Vacante quitada de favoritos.')


def pagina_postulaciones(usuario_id):
    encabezado('Mis oportunidades', 'Mis postulaciones',
               'Sigue el estado de tus candidaturas desde un solo lugar.')
    datos=postulaciones_con_estado(usuario_id)
    if not datos:
        st.info('Todavía no te has postulado a una oferta.')
        return
    estados = {'Pendiente':0,'En revisión':0,'Aceptada':0,'Rechazada':0}
    for fila in datos:
        if fila.get('estado') in estados: estados[fila['estado']] += 1
    indicadores=st.columns(4)
    for i, (estado,cantidad) in enumerate(estados.items()):
        indicadores[i].metric(estado,cantidad)
    ui_section('Historial', f'{len(datos)} candidatura(s)')
    for fila in datos:
        with st.container(border=True):
            left,right=st.columns([3.5,1])
            with left:
                st.markdown(f'**{safe(fila.get("oferta") or "Vacante")}**')
                st.caption(fila.get('empresa') or 'Empresa no especificada')
            with right:
                st.markdown(f'**{safe(fila.get("estado") or "Pendiente")}**')
                fecha=(fila.get('actualizado') or fila.get('fecha_postulacion') or '')
                st.caption(str(fecha)[:10] if fecha else 'Sin fecha')


def pagina_empresa_laboral(usuario_id, empresas_actuales):
    encabezado('VINCULACIÓN LABORAL', 'Mi empresa laboral',
               'Consulta dónde trabajas y solicita unirte o salir de una organización.')
    mensaje_pendiente()
    st.subheader('Mis empresas actuales')
    if empresas_actuales:
        for empresa in empresas_actuales:
            a,b=st.columns([4,1])
            with a:
                st.write(f'**{empresa["nombre"]}** · {empresa.get("ubicacion") or ""}')
            with b:
                solicitudes=mis_solicitudes_laborales(usuario_id)
                en_proceso=any(s['empresa_id']==empresa['id'] and s['tipo']=='SOLICITA_DESVINCULACION' and s['estado']=='Pendiente' for s in solicitudes)
                if st.button('Solicitar salida',key=f'salida_emp_{empresa["id"]}',disabled=en_proceso):
                    accion(solicitar_desvinculacion,usuario_id,empresa['id'],mensaje='Solicitud de desvinculación enviada.')
                if en_proceso:st.caption('Salida pendiente')
    else:
        st.info('Todavía no tienes una empresa vinculada.')
    st.divider()
    st.subheader('Solicitar ingreso a una empresa')
    disponibles=empresas_disponibles(usuario_id)
    if disponibles:
        for e in disponibles:
            a,b=st.columns([4,1])
            with a:
                st.write(f'**{e["nombre"]}** · {e.get("industria") or ""}')
                st.caption('Estado de solicitud: '+(e.get('estado') or 'Disponible'))
            with b:
                if st.button('Solicitar ingreso',key=f'solicitar_emp_{e["id"]}',
                             disabled=e['estado']=='Pendiente', use_container_width=True):
                    accion(solicitar_vinculacion,usuario_id,e['id'],mensaje='Solicitud enviada a la empresa.')
    else:
        st.info('No hay empresas disponibles para solicitar vinculación.')
    st.divider()
    st.subheader('Historial de solicitudes laborales')
    historial=mis_solicitudes_laborales(usuario_id)
    if historial:
        st.dataframe(historial,use_container_width=True,hide_index=True)
    else:st.caption('Aún no has realizado solicitudes.')


def pagina_solicitudes_empresa(empresa_id):
    encabezado('Gestión de personal', 'Solicitudes laborales',
               'Revisa solicitudes de ingreso y desvinculación de tu empresa.')
    mensaje_pendiente()
    pendientes=solicitudes_laborales_empresa(empresa_id)
    st.metric('Solicitudes por responder',len(pendientes))
    if not pendientes:
        st.info('No hay solicitudes laborales pendientes.')
        return
    for item in pendientes:
        texto='Solicitud de ingreso' if item['tipo']=='SOLICITA_VINCULACION' else 'Solicitud de desvinculación'
        with st.container(border=True):
            portrait_card(item.get('profesional') or 'Profesional', category=texto,
                          detail=item.get('correo') or '')
            a,b,_=st.columns([1,1,2])
            with a:
                if st.button('Aceptar',key=f'emp_aceptar_{item["tipo"]}_{item["usuario_id"]}',
                             type='primary',use_container_width=True):
                    accion(resolver_solicitud_laboral,empresa_id,item['usuario_id'],item['tipo'],True,
                           mensaje='Solicitud aprobada.')
            with b:
                if st.button('Rechazar',key=f'emp_rechazar_{item["tipo"]}_{item["usuario_id"]}',
                             use_container_width=True):
                    accion(resolver_solicitud_laboral,empresa_id,item['usuario_id'],item['tipo'],False,
                           mensaje='Solicitud rechazada.')


def pagina_candidatos_empresa(empresa_id, ofertas, sugerir):
    encabezado('Selección de personal', 'Candidatos',
               'Gestiona postulantes y descubre profesionales compatibles con tus ofertas.')
    mensaje_pendiente()
    if not ofertas:
        st.info('Publica primero una oferta en Mis vacantes.')
        return
    opciones={f'{o.get("titulo") or "Oferta"} · {o["id"]}':o['id'] for o in ofertas}
    eleccion=st.selectbox('Vacante de tu empresa',list(opciones))
    oferta_id=opciones[eleccion]
    filas=postulantes_empresa(empresa_id,oferta_id)
    st.metric('Postulaciones recibidas',len(filas))
    ui_section('Postulantes', 'Actualiza el estado de cada candidatura')
    for postulacion in filas:
        with st.container(border=True):
            portrait_card(postulacion.get('profesional') or 'Profesional',category='Candidato',
                          location=postulacion.get('ubicacion') or '',
                          detail=postulacion.get('correo') or '')
            estado=postulacion['estado']
            a,b=st.columns([3,1])
            with a:
                nuevo=st.selectbox('Estado',ESTADOS_POSTULACION,index=ESTADOS_POSTULACION.index(estado)
                    if estado in ESTADOS_POSTULACION else 0,
                    key=f'estado_cand_{oferta_id}_{postulacion["usuario_id"]}')
            with b:
                st.write('')
                if st.button('Guardar estado',key=f'guardar_estado_{oferta_id}_{postulacion["usuario_id"]}',
                             disabled=nuevo==estado,type='primary'):
                    accion(cambiar_estado_postulacion,empresa_id,oferta_id,postulacion['usuario_id'],nuevo,
                           mensaje='Se actualizó el estado del candidato.')
    if not filas:
        st.info('Esta vacante no ha recibido postulaciones todavía.')
    ui_section('Talento recomendado', 'Sugerencias basadas en conexiones y habilidades')
    sugerir(oferta_id)


def pagina_ciclo_vacantes(empresa_id, ofertas):
    if not ofertas: return
    st.divider()
    st.subheader('Cerrar o reabrir vacantes')
    st.caption('Una vacante cerrada o vencida no permite nuevas postulaciones.')
    opciones={f'{o.get("titulo") or "Oferta"} · {o["id"]}':o for o in ofertas}
    elegido=st.selectbox('Oferta a gestionar',list(opciones),key='ciclo_oferta')
    o=opciones[elegido]
    fecha_str=str(o.get('fecha_cierre') or '')[:10]
    vencida=bool(fecha_str and fecha_str < date.today().isoformat())
    st.caption(f'Estado: {o.get("estado") or "Abierta"} · Fecha de cierre: {fecha_str or "Sin fecha"}')
    a,b=st.columns(2)
    with a:
        if st.button('Cerrar esta vacante',key=f'cierra_{o["id"]}',use_container_width=True,
                     disabled=o.get('estado')=='Cerrada'):
            accion(cambiar_estado_vacante,empresa_id,o['id'],'Cerrada',None,mensaje='Vacante cerrada.')
    with b:
        nueva_fecha=st.date_input('Nueva fecha de cierre para reabrir', value=date.today()+timedelta(days=30),
                                  min_value=date.today(),key=f'fecha_reabre_{o["id"]}')
        if st.button('Reabrir vacante',key=f'reabre_{o["id"]}',type='primary',use_container_width=True,
                     disabled=o.get('estado')!='Cerrada' and not vencida):
            accion(cambiar_estado_vacante,empresa_id,o['id'],'Abierta',nueva_fecha.isoformat(),mensaje='Vacante reabierta.')


def pagina_centro_notificaciones(rol,perfil_id):
    encabezado('ACTIVIDAD DE TU RED', 'Notificaciones',
               'Avisos automáticos de solicitudes, candidaturas y proyectos.')
    mensaje_pendiente()
    eventos=notificaciones(rol,perfil_id)
    pendientes=[e for e in eventos if not e['leida']]
    st.metric('Sin leer',len(pendientes))
    if pendientes:
        if st.button('Marcar todas como leídas',type='primary'):
            accion(marcar_notificaciones_leidas,rol,perfil_id,[e['clave'] for e in pendientes],
                   mensaje='Notificaciones marcadas como leídas.')
    if not eventos:
        st.info('Por ahora no tienes notificaciones.')
        return
    for item in eventos:
        with st.container(border=True):
            x,y=st.columns([5,1])
            with x:
                st.write(('**Nuevo · **' if not item['leida'] else '')+item['texto'])
                st.caption('Revisa: '+item['seccion'])
            with y:
                if st.button('Abrir',key=f'abrir_alerta_{item["clave"]}',use_container_width=True):
                    try:
                        if not item['leida']:
                            marcar_notificaciones_leidas(rol,perfil_id,[item['clave']])
                        st.session_state['pagina_actual']=item['seccion']
                        st.rerun()
                    except Exception as exc:st.error(str(exc))


def progreso_perfil(perfil,cuantas_habilidades):
    campos=['nombre','correo','telefono','ubicacion','experiencia','educacion']
    llenos=sum(bool(str(perfil.get(c) or '').strip()) for c in campos)
    total=len(campos)+1
    puntuacion=(llenos+int(cuantas_habilidades>0))/total
    st.subheader('Tu perfil profesional')
    st.progress(puntuacion,text=f'{round(puntuacion*100)} % completado')
    if puntuacion<1:
        faltantes=[c for c in campos if not str(perfil.get(c) or '').strip()]
        if not cuantas_habilidades:faltantes.append('habilidades')
        st.caption('Para mejorar tu perfil, completa: '+', '.join(faltantes))
    else:
        st.caption('Tu perfil tiene todos los campos principales completos.')
