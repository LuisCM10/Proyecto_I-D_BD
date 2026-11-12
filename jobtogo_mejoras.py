"""Funciones de empleo y notificaciones para Job to go.

No crea nuevos tipos de nodos. Usa las relaciones del grafo existente y
propiedades opcionales para estados. Diseñado para demostración LOCAL.
Los IDs vienen de la sesión; la interfaz no acepta IDs introducidos libremente.
"""
from datetime import date
from conexion import db

ESTADOS_POSTULACION = ('Pendiente', 'En revisión', 'Aceptada', 'Rechazada')
ESTADOS_VACANTE = ('Abierta', 'Cerrada')


def leer(cypher, params=None):
    return db.ejecutar_consulta(cypher, params or {}, write=False)


def escribir(cypher, params=None):
    return db.ejecutar_consulta(cypher, params or {})


def ofertas_detalladas(usuario_id=None):
    """Todas las ofertas con requisitos, estado efectivo y coincidencias."""
    rows = leer('''
        MATCH (o:OfertaLaboral)
        OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o)
        OPTIONAL MATCH (o)-[:REQUIERE_TENER]->(h:Habilidad)
        WITH o, e, collect(DISTINCT h.nombre) AS habilidades,
             collect(DISTINCT h.id) AS habilidad_ids
        OPTIONAL MATCH (u:Usuario {id:$usuario_id})-[:POSEE]->(propia:Habilidad)
        WITH o, e, habilidades, habilidad_ids, collect(DISTINCT propia.id) AS propias
        RETURN o.id AS id, o.titulo AS titulo, o.descripcion AS descripcion,
               o.ubicacion AS ubicacion, o.salario AS salario,
               o.tipo_contrato AS tipo_contrato, toString(o.fecha_cierre) AS fecha_cierre,
               toString(o.fecha_publicacion) AS fecha_publicacion,
               coalesce(o.estado, 'Abierta') AS estado,
               e.id AS empresa_id, e.nombre AS empresa, habilidades,
               size([id_h IN habilidad_ids WHERE id_h IN propias]) AS coincidencias,
               CASE WHEN $usuario_id IS NULL THEN false ELSE
                  EXISTS { MATCH (u:Usuario {id:$usuario_id})-[:GUARDA_OFERTA]->(o) }
               END AS guardada
        ORDER BY fecha_publicacion DESC, titulo
    ''', {'usuario_id': usuario_id})
    hoy = date.today().isoformat()
    for row in rows:
        if row['estado'] == 'Cerrada':
            row['estado_visible'] = 'Cerrada'
        elif row.get('fecha_cierre') and str(row['fecha_cierre'])[:10] < hoy:
            row['estado_visible'] = 'Vencida'
        else:
            row['estado_visible'] = 'Abierta'
    return rows


def favoritos(usuario_id):
    return leer('''
        MATCH (u:Usuario {id:$usuario_id})-[:GUARDA_OFERTA]->(o:OfertaLaboral)
        OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o)
        RETURN o.id AS id, o.titulo AS titulo, e.nombre AS empresa,
               o.ubicacion AS ubicacion, o.salario AS salario,
               toString(o.fecha_cierre) AS fecha_cierre,
               coalesce(o.estado,'Abierta') AS estado
        ORDER BY titulo
    ''', {'usuario_id': usuario_id})


def guardar_favorito(usuario_id, oferta_id):
    rows = escribir('''
        MATCH (u:Usuario {id:$usuario_id}), (o:OfertaLaboral {id:$oferta_id})
        MERGE (u)-[r:GUARDA_OFERTA]->(o)
        ON CREATE SET r.guardada_en = toString(datetime())
        RETURN o.id AS id
    ''', {'usuario_id': usuario_id, 'oferta_id': oferta_id})
    if not rows:
        raise ValueError('No se encontró el profesional o la vacante.')
    return rows[0]


def quitar_favorito(usuario_id, oferta_id):
    rows = escribir('''
        MATCH (u:Usuario {id:$usuario_id})-[r:GUARDA_OFERTA]->(o:OfertaLaboral {id:$oferta_id})
        WITH o.id AS id, r DELETE r RETURN id
    ''', {'usuario_id': usuario_id, 'oferta_id': oferta_id})
    if not rows:
        raise ValueError('Esta vacante ya no está guardada.')
    return rows[0]


def postulaciones_con_estado(usuario_id):
    return leer('''
        MATCH (u:Usuario {id:$usuario_id})-[r:SE_POSTULA_A|POSTULA_A]->(o:OfertaLaboral)
        OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o)
        RETURN DISTINCT o.id AS id, o.titulo AS oferta, e.nombre AS empresa,
               coalesce(r.estado,'Pendiente') AS estado,
               toString(r.fecha_postulacion) AS fecha_postulacion,
               toString(r.fecha_actualizacion) AS actualizado
        ORDER BY oferta
    ''', {'usuario_id': usuario_id})


def postular_vacante(usuario_id, oferta_id):
    rows = escribir('''
        MATCH (u:Usuario {id:$usuario_id}), (o:OfertaLaboral {id:$oferta_id})
        WHERE coalesce(o.estado, 'Abierta') = 'Abierta'
          AND (o.fecha_cierre IS NULL OR toString(o.fecha_cierre) >= toString(date()))
          AND NOT EXISTS { MATCH (u)-[:SE_POSTULA_A|POSTULA_A]->(o) }
        CREATE (u)-[r:SE_POSTULA_A {estado:'Pendiente',fecha_postulacion:toString(datetime())}]->(o)
        RETURN o.id AS id
    ''', {'usuario_id': usuario_id, 'oferta_id': oferta_id})
    if not rows:
        raise ValueError('La vacante está cerrada/vencida, ya te postulaste o no existe.')
    return rows[0]


def postulantes_empresa(empresa_id, oferta_id):
    return leer('''
        MATCH (e:Empresa {id:$empresa_id})-[:PUBLICA]->(o:OfertaLaboral {id:$oferta_id})
        MATCH (u:Usuario)-[r:SE_POSTULA_A|POSTULA_A]->(o)
        RETURN u.id AS usuario_id, u.nombre AS profesional,
               u.correo AS correo, u.ubicacion AS ubicacion,
               coalesce(r.estado,'Pendiente') AS estado,
               toString(r.fecha_postulacion) AS fecha
        ORDER BY profesional
    ''', {'empresa_id': empresa_id, 'oferta_id': oferta_id})


def cambiar_estado_postulacion(empresa_id, oferta_id, usuario_id, estado):
    if estado not in ESTADOS_POSTULACION:
        raise ValueError('Estado de postulación no permitido.')
    rows = escribir('''
        MATCH (e:Empresa {id:$empresa_id})-[:PUBLICA]->(o:OfertaLaboral {id:$oferta_id})
        MATCH (u:Usuario {id:$usuario_id})-[r:SE_POSTULA_A|POSTULA_A]->(o)
        SET r.estado=$estado, r.fecha_actualizacion=toString(datetime())
        RETURN r.estado AS estado, u.id AS usuario_id
    ''', {'empresa_id': empresa_id, 'oferta_id': oferta_id,
          'usuario_id': usuario_id, 'estado': estado})
    if not rows:
        raise ValueError('Candidatura no encontrada o la vacante no pertenece a esta empresa.')
    return rows[0]


def cambiar_estado_vacante(empresa_id, oferta_id, estado, nueva_fecha=None):
    if estado not in ESTADOS_VACANTE:
        raise ValueError('Estado no permitido.')
    if nueva_fecha is not None:
        try:
            fecha = date.fromisoformat(str(nueva_fecha)).isoformat()
        except ValueError:
            raise ValueError('Fecha de cierre inválida.')
        if estado == 'Abierta' and fecha < date.today().isoformat():
            raise ValueError('Para reabrir una vacante, elige una fecha futura.')
    else:
        fecha = None
    rows = escribir('''
        MATCH (e:Empresa {id:$empresa_id})-[:PUBLICA]->(o:OfertaLaboral {id:$oferta_id})
        SET o.estado=$estado, o.fecha_cierre=coalesce($fecha_cierre,o.fecha_cierre),
            o.estado_actualizado_en=toString(datetime())
        RETURN o.id AS id, o.estado AS estado
    ''', {'empresa_id': empresa_id, 'oferta_id': oferta_id,
          'estado': estado, 'fecha_cierre': fecha})
    if not rows:
        raise ValueError('No puedes modificar esta oferta.')
    return rows[0]


def empresas_disponibles(usuario_id):
    return leer('''
        MATCH (e:Empresa)
        WHERE NOT EXISTS { MATCH (:Usuario {id:$usuario_id})-[:TRABAJA_EN]->(e) }
        OPTIONAL MATCH (u:Usuario {id:$usuario_id})-[s:SOLICITA_VINCULACION]->(e)
        RETURN e.id AS id, e.nombre AS nombre, e.industria AS industria,
               coalesce(s.estado,'Disponible') AS estado
        ORDER BY nombre
    ''', {'usuario_id': usuario_id})


def mis_solicitudes_laborales(usuario_id):
    return leer('''
        MATCH (u:Usuario {id:$usuario_id})-[r:SOLICITA_VINCULACION|SOLICITA_DESVINCULACION]->(e:Empresa)
        RETURN e.id AS empresa_id, e.nombre AS empresa,
               type(r) AS tipo, coalesce(r.estado,'Pendiente') AS estado,
               toString(r.fecha_solicitud) AS fecha,
               toString(r.fecha_respuesta) AS fecha_respuesta
        ORDER BY empresa
    ''', {'usuario_id': usuario_id})


def solicitar_vinculacion(usuario_id, empresa_id):
    rows = escribir('''
        MATCH (u:Usuario {id:$usuario_id}), (e:Empresa {id:$empresa_id})
        WHERE NOT EXISTS { MATCH (u)-[:TRABAJA_EN]->(e) }
        MERGE (u)-[r:SOLICITA_VINCULACION]->(e)
        SET r.estado='Pendiente',r.fecha_solicitud=toString(datetime()),
            r.fecha_respuesta=null
        RETURN e.id AS id
    ''', {'usuario_id':usuario_id,'empresa_id':empresa_id})
    if not rows:
        raise ValueError('Ya trabajas en esta empresa o no existe el perfil.')
    return rows[0]


def solicitar_desvinculacion(usuario_id, empresa_id):
    rows = escribir('''
        MATCH (u:Usuario {id:$usuario_id})-[:TRABAJA_EN]->(e:Empresa {id:$empresa_id})
        MERGE (u)-[r:SOLICITA_DESVINCULACION]->(e)
        SET r.estado='Pendiente',r.fecha_solicitud=toString(datetime()),
            r.fecha_respuesta=null
        RETURN e.id AS id
    ''', {'usuario_id':usuario_id,'empresa_id':empresa_id})
    if not rows:
        raise ValueError('No hay relación laboral con esta empresa.')
    return rows[0]


def solicitudes_laborales_empresa(empresa_id):
    return leer('''
        MATCH (u:Usuario)-[r:SOLICITA_VINCULACION|SOLICITA_DESVINCULACION]->(e:Empresa {id:$empresa_id})
        WHERE coalesce(r.estado,'Pendiente')='Pendiente'
        RETURN u.id AS usuario_id, u.nombre AS profesional, u.correo AS correo,
               type(r) AS tipo, toString(r.fecha_solicitud) AS fecha
        ORDER BY tipo, profesional
    ''', {'empresa_id':empresa_id})


def resolver_solicitud_laboral(empresa_id, usuario_id, tipo, aceptar):
    if tipo not in ('SOLICITA_VINCULACION','SOLICITA_DESVINCULACION'):
        raise ValueError('Tipo de solicitud incorrecto.')
    # Tipos elegidos de catálogo fijo, no ingresados por el usuario.
    if tipo == 'SOLICITA_VINCULACION':
        rows = escribir('''
            MATCH (u:Usuario {id:$usuario_id})-[r:SOLICITA_VINCULACION]->(e:Empresa {id:$empresa_id})
            WHERE coalesce(r.estado,'Pendiente')='Pendiente'
            FOREACH (_ IN CASE WHEN $aceptar THEN [1] ELSE [] END |
                MERGE (u)-[:TRABAJA_EN]->(e))
            SET r.estado=CASE WHEN $aceptar THEN 'Aceptada' ELSE 'Rechazada' END,
                r.fecha_respuesta=toString(datetime())
            RETURN r.estado AS estado
        ''', {'usuario_id':usuario_id,'empresa_id':empresa_id,'aceptar':bool(aceptar)})
    else:
        rows = escribir('''
            MATCH (u:Usuario {id:$usuario_id})-[r:SOLICITA_DESVINCULACION]->(e:Empresa {id:$empresa_id})
            WHERE coalesce(r.estado,'Pendiente')='Pendiente'
            OPTIONAL MATCH (u)-[trabajo:TRABAJA_EN]->(e)
            FOREACH (_ IN CASE WHEN $aceptar AND trabajo IS NOT NULL THEN [1] ELSE [] END |
                DELETE trabajo)
            SET r.estado=CASE WHEN $aceptar THEN 'Aceptada' ELSE 'Rechazada' END,
                r.fecha_respuesta=toString(datetime())
            RETURN r.estado AS estado
        ''', {'usuario_id':usuario_id,'empresa_id':empresa_id,'aceptar':bool(aceptar)})
    if not rows:
        raise ValueError('La solicitud ya fue atendida o no te corresponde.')
    return rows[0]


def notificaciones(rol, perfil_id):
    """Alertas derivadas de relaciones reales; solo para el perfil indicado.

    notificaciones_vistas se guarda como propiedad de Usuario/Empresa, evitando
    nuevas entidades o tablas auxiliares. No revela datos de otras cuentas.
    """
    if rol == 'profesional':
        eventos = []
        for r in leer('''
            MATCH (otro:Usuario)-[s:SOLICITA_CONEXION]->(u:Usuario {id:$id})
            RETURN otro.id AS ref, otro.nombre AS nombre, toString(s.enviada_en) AS fecha
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'contacto:{r["ref"]}', 'texto':f'{r["nombre"]} quiere conectar contigo', 'seccion':'Mi red'})
        for r in leer('''
            MATCH (u:Usuario {id:$id})-[c:CONECTA_CON]->(otro:Usuario)
            WHERE c.aceptada_en IS NOT NULL
            RETURN otro.id AS ref, otro.nombre AS nombre,
                   toString(c.aceptada_en) AS fecha
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'contacto-aceptado:{r["ref"]}',
                           'texto':f'{r["nombre"]} aceptó tu solicitud de conexión',
                           'seccion':'Mi red'})
        for r in leer('''
            MATCH (u:Usuario {id:$id})-[s:SE_POSTULA_A|POSTULA_A]->(o:OfertaLaboral)
            WHERE s.estado IN ['En revisión','Aceptada','Rechazada']
            RETURN o.id AS ref, o.titulo AS titulo, s.estado AS estado
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'candidatura:{r["ref"]}:{r["estado"]}', 'texto':f'Tu postulación a {r["titulo"]}: {r["estado"]}', 'seccion':'Mis postulaciones'})
        for r in leer('''
            MATCH (u:Usuario {id:$id})-[s:SOLICITA_VINCULACION|SOLICITA_DESVINCULACION]->(e:Empresa)
            WHERE s.estado IN ['Aceptada','Rechazada']
            RETURN e.id AS ref, e.nombre AS empresa, type(s) AS tipo, s.estado AS estado
        ''', {'id': perfil_id}):
            solicitud = 'vinculación' if r['tipo'] == 'SOLICITA_VINCULACION' else 'desvinculación'
            eventos.append({'clave':f'laboral:{r["ref"]}:{r["tipo"]}:{r["estado"]}', 'texto':f'Tu solicitud de {solicitud} a {r["empresa"]}: {r["estado"]}', 'seccion':'Mi empresa laboral'})
        for r in leer('''
            MATCH (u:Usuario {id:$id})-[r:PARTICIPA_EN]->(p:Proyecto)
            WHERE r.aprobada_en IS NOT NULL
            RETURN p.id AS ref, p.nombre AS proyecto, toString(r.aprobada_en) AS fecha
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'proyecto:{r["ref"]}', 'texto':f'Te aceptaron en el proyecto {r["proyecto"]}', 'seccion':'Proyectos de mi empresa'})
    elif rol == 'empresa':
        eventos = []
        for r in leer('''
            MATCH (u:Usuario)-[s:SOLICITA_VINCULACION|SOLICITA_DESVINCULACION]->(e:Empresa {id:$id})
            WHERE coalesce(s.estado,'Pendiente')='Pendiente'
            RETURN u.id AS ref, u.nombre AS nombre, type(s) AS tipo
        ''', {'id': perfil_id}):
            tipo = 'ingreso' if r['tipo'] == 'SOLICITA_VINCULACION' else 'salida'
            eventos.append({'clave':f'sol-laboral:{r["ref"]}:{r["tipo"]}', 'texto':f'{r["nombre"]} solicita {tipo} de la empresa', 'seccion':'Solicitudes laborales'})
        for r in leer('''
            MATCH (e:Empresa {id:$id})-[:TIENE]->(p:Proyecto)<-[:SOLICITA_PARTICIPACION]-(u:Usuario)
            RETURN u.id AS usuario, p.id AS proyecto_id, u.nombre AS nombre, p.nombre AS proyecto
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'proyecto-pend:{r["usuario"]}:{r["proyecto_id"]}', 'texto':f'{r["nombre"]} solicita unirse a {r["proyecto"]}', 'seccion':'Mis proyectos'})
        for r in leer('''
            MATCH (e:Empresa {id:$id})-[:PUBLICA]->(o:OfertaLaboral)<-[s:SE_POSTULA_A|POSTULA_A]-(u:Usuario)
            RETURN u.id AS usuario, o.id AS oferta_id, u.nombre AS nombre, o.titulo AS titulo
        ''', {'id': perfil_id}):
            eventos.append({'clave':f'nueva-candidatura:{r["usuario"]}:{r["oferta_id"]}', 'texto':f'{r["nombre"]} se postuló a {r["titulo"]}', 'seccion':'Candidatos'})
    else:
        return []
    etiqueta = 'Usuario' if rol == 'profesional' else 'Empresa'
    vistos = leer(f'''MATCH (n:{etiqueta} {{id:$id}}) RETURN coalesce(n.notificaciones_vistas, []) AS vistos''', {'id': perfil_id})
    leidos = set(vistos[0]['vistos'] if vistos else [])
    for item in eventos:
        item['leida'] = item['clave'] in leidos
    return eventos


def marcar_notificaciones_leidas(rol, perfil_id, claves):
    if rol not in ('profesional','empresa'):
        raise ValueError('Perfil no permitido.')
    etiqueta = 'Usuario' if rol == 'profesional' else 'Empresa'
    return escribir(f'''
        MATCH (n:{etiqueta} {{id:$id}})
        SET n.notificaciones_vistas = reduce(acc = coalesce(n.notificaciones_vistas, []),
            clave IN $claves | CASE WHEN clave IN acc THEN acc ELSE acc + clave END)
        RETURN size(n.notificaciones_vistas) AS total
    ''', {'id': perfil_id, 'claves': list(dict.fromkeys(claves))})
