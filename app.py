"""Job to go · Aplicación visual para el I+D de Bases de Datos.

Iniciar con: streamlit run app.py
La aplicación consulta Neo4j directamente y reutiliza las clases del repositorio.
"""
import html
import os
import hmac
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from pyvis.network import Network
from jobtogo_ui import (inject_theme, hero as ui_hero, section as ui_section,
                         portrait_card, job_card, safe as ui_safe, initials as ui_initials)

from conexion import db
from jobtogo_mejoras import notificaciones, postulaciones_con_estado, ofertas_detalladas
from jobtogo_pantallas_mejoras import (
    pagina_busqueda, pagina_favoritos, pagina_postulaciones,
    pagina_empresa_laboral, pagina_solicitudes_empresa,
    pagina_candidatos_empresa, pagina_ciclo_vacantes,
    pagina_centro_notificaciones, progreso_perfil,
)
from jobtogo_operaciones import (
    crear_perfil, actualizar_profesional,
    actualizar_empresa, consultar_postulaciones, postularse,
    publicar_vacante, editar_vacante_propietaria,
    habilidades_catalogo, ids_habilidades_usuario,
    actualizar_habilidades_profesional, proyectos_de_empresa,
    tecnologias_catalogo, crear_proyecto_empresa, editar_proyecto_empresa,
    revertir_perfil_nuevo,
    profesionales_para_conectar, solicitudes_recibidas, solicitudes_enviadas,
    contactos_de_profesional, solicitar_conexion, aceptar_solicitud,
    rechazar_solicitud, cancelar_solicitud,
    empresas_de_profesional, empleados_de_empresa,
    proyectos_para_profesional, participaciones_de_profesional,
    solicitar_participacion_proyecto, cancelar_participacion_proyecto,
    solicitudes_proyectos_empresa, participantes_proyectos_empresa,
    aceptar_participacion_proyecto, rechazar_participacion_proyecto,
)
from entidades.controller import crear_restricciones_unicidad
from entidades.usuario import Usuario
from entidades.empresa import Empresa
from entidades.habilidad import Habilidad
from entidades.proyecto import Proyecto
from entidades.oferta_laboral import OfertaLaboral
from entidades.tecnologia import Tecnologia
from consultas_grafo import ConsultasGrafo
from consultas.CaminosYConexiones import CaminosYConexiones
from consultas.PanelAnalitica import PanelAnalitica
from consultas.StmRecomendacion import SistemaRecomendacion
from servicios_gui import (
    listar_entidades, total_entidades, total_relaciones, ultimas_ofertas,
    datos_grafo, habilidades_de_usuario, postulaciones_de_usuario,
)

load_dotenv()
st.set_page_config(
    page_title="Job to go | Red profesional inteligente",
    layout="wide",
    initial_sidebar_state="locked",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
:root {--jt-bg:#f6f9fd;--jt-white:#ffffff;--jt-blue:#2563eb;--jt-blue-dark:#1d4ed8;--jt-ink:#172b4d;--jt-muted:#627692;--jt-border:#dce6f3;--jt-light:#edf4ff;}
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif;}
.stApp {background:#f6f9fd;color:#172b4d;}
[data-testid="stHeader"] {background:rgba(246,249,253,.92);backdrop-filter:blur(12px);}
[data-testid="stToolbar"], [data-testid="stDeployButton"], #MainMenu, footer {display:none !important;}
[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #dce6f3;}
[data-testid="stSidebar"] > div:first-child {background:#ffffff;}
[data-testid="stSidebar"] .stMarkdown h3 {color:#172b4d;}
.block-container {max-width:1460px;padding:1.25rem 2rem 3rem;}
h1,h2,h3,h4 {font-family:'Manrope','DM Sans',sans-serif;letter-spacing:-.032em;color:#172b4d;}
h2,h3 {font-weight:800;}
.stMarkdown p,.stCaption {line-height:1.6;}
.eyebrow {font-size:11px;line-height:1.4;letter-spacing:2.3px;text-transform:uppercase;font-weight:800;color:#2563eb;}
.hero {position:relative;overflow:hidden;background:linear-gradient(120deg,#ffffff 0%,#f6faff 55%,#e8f2ff 100%);border:1px solid #d5e5fa;border-radius:20px;padding:30px 35px;margin:0 0 19px;box-shadow:0 9px 26px rgba(31,85,160,.055);}
.hero:after {content:'';position:absolute;right:-85px;top:-145px;width:375px;height:375px;background:radial-gradient(circle,rgba(55,119,232,.12),transparent 68%);pointer-events:none;}
.hero h1 {font-size:clamp(29px,2.9vw,40px);font-weight:800;line-height:1.2;margin:12px 0 9px;color:#15325d;}
.hero p {margin:0;color:#536a89;font-size:14px;max-width:760px;}
.intro,.rp-context {color:#617692;}
.rp-section,.rp-subheading {display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin:18px 0 11px;}
.rp-section h3,.rp-subheading h3 {font-size:20px;margin:0;color:#19395f;}
.rp-section span,.rp-subheading span {color:#778aa3;font-size:12px;}
.rp-kpis {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:13px;margin:13px 0;}
.rp-kpi {position:relative;min-width:0;overflow:hidden;background:#fff;border:1px solid #dfebf7;border-radius:16px;padding:18px 20px 16px;box-shadow:0 6px 20px rgba(38,83,155,.055);}
.rp-kpi:before {content:'';position:absolute;left:0;top:0;right:0;height:3px;background:var(--kpi-accent,#3b82f6);}
.rp-kpi-icon {display:inline-flex;align-items:center;justify-content:center;width:33px;height:33px;border-radius:9px;background:#eaf2ff;color:#2563eb;font-size:11px;font-weight:800;letter-spacing:.6px;margin-bottom:11px;}
.rp-kpi .rp-kpi-number {font-size:30px;font-family:'Manrope',sans-serif;font-weight:800;line-height:1.05;color:#17365f;}
.rp-kpi .rp-kpi-label {font-size:12px;color:#627793;margin-top:7px;font-weight:650;}
.rp-network {display:inline-flex;align-items:center;gap:10px;border:1px solid #d4e5fc;border-radius:999px;background:#ecf4ff;padding:9px 15px;color:#476487;font-size:12px;font-weight:650;margin:7px 0 13px;}
.rp-network b {color:#1d4ed8;font-size:13px;}
.panel {background:#fff;border:1px solid #dde8f6;border-radius:15px;padding:18px 20px;margin:8px 0;}
.panel h4 {margin:0 0 8px;}.panel p {color:#617692;font-size:13px;margin:0;}
.chip {display:inline-block;background:#eaf2ff;color:#1d58ba;border-radius:999px;padding:4px 10px;font-size:11px;font-weight:700;}
[data-testid="stMetric"] {background:#fff;border:1px solid #deebf9;padding:17px;border-radius:15px;box-shadow:0 5px 17px rgba(38,83,155,.04);}
[data-testid="stMetricValue"] {font-weight:800;color:#17365f;}
[data-testid="stDataFrame"],[data-testid="stForm"] {border:1px solid #dbe6f2 !important;border-radius:14px;overflow:hidden;background:#fff;}
[data-testid="stForm"] {padding:16px !important;}
[data-testid="stExpander"] {border:1px solid #dce6f3;border-radius:12px;background:#fff;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:15px;}
.stButton>button,.stFormSubmitButton>button {border-radius:10px;font-weight:650;transition:background .14s ease,transform .14s ease,border-color .14s ease;}
.stButton>button:hover,.stFormSubmitButton>button:hover {transform:translateY(-1px);}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {background:#2563eb !important;color:white !important;border:1px solid #2563eb !important;box-shadow:0 4px 10px rgba(37,99,235,.13);font-weight:750;}
.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover {background:#1d4ed8 !important;}
[data-baseweb="tab-list"] {gap:8px;border-bottom:1px solid #dbe6f2;overflow-x:auto;}
[data-baseweb="tab"] {border-radius:9px 9px 0 0;font-weight:700;white-space:nowrap;}
[data-baseweb="tab"][aria-selected="true"] {color:#1d4ed8;}
[data-baseweb="input"],[data-baseweb="select"] {border-radius:9px;}
.rp-bars {border:1px solid #dbe8f7;background:#fff;padding:19px 20px;border-radius:16px;min-height:260px;}
.rp-bar-row {display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1.7fr) 28px;align-items:center;gap:10px;margin:12px 0;}
.rp-bar-name {font-size:12px;color:#354f72;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.rp-bar-track {height:11px;border-radius:999px;background:#eaf1fb;overflow:hidden;}
.rp-bar-fill {height:100%;border-radius:999px;background:var(--bar-color,#3b82f6);min-width:3px;}
.rp-bar-value {font-size:12px;color:#27476e;text-align:right;font-weight:800;font-variant-numeric:tabular-nums;}
.rp-mini-stat {display:flex;align-items:center;flex-wrap:wrap;gap:10px;background:#edf5ff;border:1px solid #d9e8fc;border-radius:12px;padding:12px 15px;color:#476487;font-size:13px;}
.rp-mini-stat strong {color:#1d4ed8;font-size:19px;}
.rp-card-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:13px 0;}
.rp-result {min-width:0;border:1px solid #dce8f7;border-radius:16px;background:#fff;padding:19px 21px;box-shadow:0 5px 16px rgba(38,83,155,.045);}
.rp-result-top {display:flex;justify-content:space-between;gap:12px;align-items:flex-start;}
.rp-result .rp-category {font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-weight:800;color:#2368d9;}
.rp-result h4 {margin:8px 0 9px;font-size:18px;line-height:1.35;font-weight:800;color:#16345b;overflow-wrap:anywhere;}
.rp-result p {font-size:12px;color:#607694;margin:5px 0;line-height:1.55;}
.rp-score {background:#e8f2ff;border:1px solid #c5ddff;color:#1d59af;border-radius:999px;white-space:nowrap;padding:5px 9px;font-size:11px;font-weight:800;}
.rp-tags {display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;}
.rp-tag {display:inline-block;background:#f0f6ff;border:1px solid #d7e7fe;padding:5px 9px;border-radius:999px;color:#2c5c9b;font-size:11px;}
.rp-muted {color:#758aa6 !important;}
.rp-path {display:flex;gap:7px;align-items:stretch;flex-wrap:wrap;margin:14px 0 8px;}
.rp-path-node {flex:1 1 158px;min-width:132px;max-width:320px;background:#fff;border:1px solid #d4e5f8;border-radius:14px;padding:14px 16px;}
.rp-path-node .rp-path-kind {font-size:10px;letter-spacing:1.35px;text-transform:uppercase;color:#2563eb;font-weight:800;}
.rp-path-node .rp-path-name {font-size:13px;font-weight:750;color:#1e426d;margin-top:5px;line-height:1.4;overflow-wrap:anywhere;}
.rp-path-arrow {align-self:center;color:#487cbe;display:flex;flex-direction:column;gap:1px;text-align:center;}
.rp-path-arrow b {font-size:18px;line-height:1;}
.rp-path-arrow small {font-size:9px;color:#6c84a4;max-width:92px;overflow-wrap:anywhere;}
.rp-legend {display:flex;gap:9px;flex-wrap:wrap;margin:11px 0;}
.rp-legend-item {border:1px solid #d8e6f6;border-radius:999px;padding:7px 11px;font-size:11px;color:#365578;background:#fff;}
.rp-dot {width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:7px;background:var(--dot-color);}
.rp-footnote {padding:13px 16px;background:#edf5ff;border-left:3px solid #2563eb;border-radius:9px;color:#476487;font-size:12px;margin:10px 0 16px;line-height:1.6;}
[data-testid="stSidebar"] [data-testid="stButton"] {margin:2px 0;}
[data-testid="stSidebar"] [data-testid="stButton"] button {width:100%;min-height:40px;display:flex;align-items:center;justify-content:flex-start;text-align:left;border-radius:10px;padding:9px 14px;border:1px solid transparent;box-shadow:none;color:#4c6484;background:transparent;font-size:13px;font-weight:650;transition:background .14s ease,border-color .14s ease,color .14s ease;}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {background:#ecf4ff;color:#1d4ed8;border-color:#d7e7fe;transform:none;}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {background:#e6f0ff !important;color:#1556b5 !important;border:1px solid #c9defa !important;box-shadow:inset 3px 0 0 #2563eb;font-weight:800;}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {background:#d9e9ff !important;}
[data-testid="stSidebar"] .jtg-sidebar-caption {font-size:10px;font-weight:800;color:#8da1b9;letter-spacing:1.8px;text-transform:uppercase;margin:18px 0 7px;}
[data-testid="stSidebar"] .jtg-brand {font-family:'Manrope','DM Sans',sans-serif;font-size:26px;font-weight:800;letter-spacing:-1px;color:#1d4ed8;padding:6px 0 2px;}
/* Mantener siempre localizable el botón para recuperar el menú lateral */
[data-testid="stSidebarCollapsedControl"] button {background:#fff !important;color:#1d4ed8 !important;border:1px solid #bfd4f5 !important;border-radius:10px !important;box-shadow:0 3px 10px rgba(26,79,158,.1) !important;}
@media(max-width:1100px) {.rp-kpis{grid-template-columns:repeat(3,minmax(0,1fr));}}
@media(max-width:850px) {.rp-card-grid{grid-template-columns:1fr;}.block-container{padding:1.1rem 1rem 2rem;}}
@media(max-width:700px) {.hero{padding:24px 21px;}.rp-kpis{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;}.rp-kpi{padding:15px;}.rp-kpi .rp-kpi-number{font-size:27px;}.rp-path-node{flex-basis:100%;max-width:none;}.rp-bars{padding:13px;}.rp-bar-row{gap:7px;}}
</style>
""", unsafe_allow_html=True)

# Estilos y componentes visuales de la nueva identidad de Job to go.
inject_theme()

REPOS = {
    "Usuarios": Usuario(),
    "Empresas": Empresa(),
    "Habilidades": Habilidad(),
    "Proyectos": Proyecto(),
    "Ofertas laborales": OfertaLaboral(),
    "Tecnologías": Tecnologia(),
}
CAMPOS = {
    "Usuarios": [
        ("nombre", "Nombre completo", "text"), ("correo", "Correo electrónico", "text"),
        ("telefono", "Teléfono", "text"), ("ubicacion", "Ubicación", "text"),
        ("experiencia", "Experiencia", "area"), ("educacion", "Educación", "area"),
    ],
    "Empresas": [
        ("nombre", "Nombre de la empresa", "text"), ("industria", "Industria", "text"),
        ("ubicacion", "Ubicación", "text"), ("tamano", "Tamaño", "text"),
        ("descripcion", "Descripción", "area"),
    ],
    "Habilidades": [
        ("nombre", "Nombre de habilidad", "text"), ("categoria", "Categoría", "text"),
        ("nivel", "Nivel", "text"),
    ],
    "Proyectos": [
        ("nombre", "Nombre del proyecto", "text"), ("descripcion", "Descripción", "area"),
        ("fecha_inicio", "Fecha de inicio (AAAA-MM-DD)", "text"),
        ("fecha_fin", "Fecha de finalización (AAAA-MM-DD)", "text"),
        ("tecnologias", "Tecnologías (separadas por coma)", "text"),
    ],
    "Ofertas laborales": [
        ("titulo", "Título de la oferta", "text"), ("descripcion", "Descripción", "area"),
        ("fecha_publicacion", "Fecha de publicación (AAAA-MM-DD)", "text"),
        ("fecha_cierre", "Fecha de cierre (AAAA-MM-DD)", "text"),
        ("ubicacion", "Ubicación", "text"), ("salario", "Salario (COP)", "number"),
        ("tipo_contrato", "Tipo de contrato", "text"),
    ],
    "Tecnologías": [
        ("nombre", "Nombre", "text"), ("categoria", "Categoría", "text"),
        ("descripcion", "Descripción", "area"),
    ],
}
NOMBRE = {
    "Usuarios": "nombre", "Empresas": "nombre", "Habilidades": "nombre",
    "Proyectos": "nombre", "Ofertas laborales": "titulo", "Tecnologías": "nombre",
}



def limpio(valor):
    """Representación segura para la web; nunca interpreta HTML de la BD."""
    return html.escape(str(valor if valor is not None else ""))


def lista_textos(valor):
    if valor is None:
        return []
    if isinstance(valor, (list, tuple, set)):
        return [str(v) for v in valor if v is not None and str(v).strip()]
    return [str(valor)] if str(valor).strip() else []


def iconos(tipo):
    return {"Usuario":"Profesional", "Empresa":"Empresa", "Habilidad":"Habilidad", "Proyecto":"Proyecto", "OfertaLaboral":"Vacante", "Tecnologia":"Tecnología"}.get(tipo,"Nodo")


def titulo_sec(titulo, ayuda=""):
    ui_section(titulo, ayuda)


def bloques_barras(datos, clave_nombre, clave_valor, color="#8595ff"):
    """Barras HTML para no recortar nombres largos y no depender de otra librería."""
    if not datos:
        st.info("No hay suficientes datos para mostrar esta estadística.")
        return
    maximo=max([float(x.get(clave_valor) or 0) for x in datos] or [1]) or 1
    filas=[]
    for fila in datos:
        nombre=limpio(fila.get(clave_nombre) or "Sin nombre")
        valor=float(fila.get(clave_valor) or 0)
        pct=max(0,min(100,100*valor/maximo))
        numero=int(valor) if valor.is_integer() else valor
        filas.append(f'<div class="rp-bar-row" title="{nombre}"><div class="rp-bar-name" title="{nombre}">{nombre}</div>'
                     f'<div class="rp-bar-track"><div class="rp-bar-fill" style="width:{pct:.1f}%;--bar-color:{color}"></div></div>'
                     f'<div class="rp-bar-value">{numero}</div></div>')
    st.markdown('<div class="rp-bars">'+''.join(filas)+'</div>',unsafe_allow_html=True)


def tarjetas(datos, categoria, titulo_key, campos, score_key=None, lista_key=None, score_label="coincidencias"):
    if not datos:
        st.info("No se encontraron resultados para esta selección.")
        return
    tarjetas_html=[]
    for dato in datos:
        nombre=limpio(dato.get(titulo_key) or "Sin nombre")
        valor=dato.get(score_key) if score_key else None
        score=f'<span class="rp-score">{limpio(valor)} {limpio(score_label)}</span>' if valor is not None else ''
        desc=''.join(f'<p><strong>{limpio(etiqueta)}:</strong> {limpio(dato.get(clave) if dato.get(clave) is not None else "Sin conexión identificada")}</p>' for etiqueta,clave in campos)
        chips=''.join(f'<span class="rp-tag">{limpio(x)}</span>' for x in lista_textos(dato.get(lista_key))) if lista_key else ''
        if lista_key and not chips:chips='<span class="rp-tag">Sin habilidades coincidentes</span>'
        tarjetas_html.append(f'<div class="rp-result"><div class="rp-result-top"><div class="rp-category">{limpio(categoria)}</div>{score}</div>'
                             f'<h4>{nombre}</h4>{desc}<div class="rp-tags">{chips}</div></div>')
    st.markdown('<div class="rp-card-grid">'+''.join(tarjetas_html)+'</div>',unsafe_allow_html=True)
    with st.expander('Ver resultados en tabla · detalle técnico'):
        ver_tabla(datos)


def banner(etiqueta, titulo, descripcion):
    ui_hero(etiqueta, titulo, descripcion)


def ver_tabla(datos, vacio="Todavía no hay información para mostrar."):
    if not datos:
        st.info(vacio)
        return
    df = pd.DataFrame(datos).copy()
    if 'distancia_red' in df.columns:
        df['distancia_red'] = df['distancia_red'].apply(lambda v: 'Sin ruta identificada' if pd.isna(v) else str(int(v)) if isinstance(v,(int,float)) else str(v))
    nombres={
        'usuario1':'Profesional 1','usuario2':'Profesional 2','usuario1_id':'ID 1',
        'usuario2_id':'ID 2','cantidad_habilidades':'Coincidencias',
        'habilidades_comunes':'Habilidades compartidas', 'habilidades_match':'Habilidades coincidentes',
        'habilidades_coincidentes':'Habilidades coincidentes','proyecto1':'Proyecto 1',
        'proyecto2':'Proyecto 2','tecnologias_comunes':'Tecnologías compartidas',
        'miembros_comunes':'Miembros comunes','miembros_conectados':'Miembros conectados',
        'grados_de_separacion':'Grados de separación','amigos_en_comun':'Contactos en común',
        'puntaje_relevancia':'Relevancia', 'competencias_coincidentes':'Coincidencias',
        'distancia_red':'Distancia en red','titulo_oferta':'Oferta laboral',
        'nombre':'Nombre','titulo':'Título','empresa':'Empresa', 'correo':'Correo',
        'experiencia':'Experiencia','educacion':'Educación','ubicacion':'Ubicación',
    }
    # La misma clave Cypher puede representar una cantidad (empleos) o una
    # lista de habilidades (candidatos). En Streamlit/Arrow los nombres de
    # columnas deben ser únicos, incluso cuando son traducciones visuales.
    if 'habilidades_coincidentes' in df.columns:
        valores = df['habilidades_coincidentes'].dropna()
        es_cantidad = not valores.empty and valores.map(
            lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
        ).all()
        if es_cantidad:
            nombres['habilidades_coincidentes'] = 'Cantidad de coincidencias'

    # Evitar nombres duplicados de manera general para las futuras consultas.
    columnas = []
    repeticiones = {}
    for original in df.columns:
        etiqueta = str(nombres.get(original, original))
        repeticiones[etiqueta] = repeticiones.get(etiqueta, 0) + 1
        if repeticiones[etiqueta] > 1:
            etiqueta = f'{etiqueta} ({repeticiones[etiqueta]})'
        columnas.append(etiqueta)
    df.columns = columnas
    st.dataframe(df, use_container_width=True, hide_index=True)


def lista(seccion):
    return [x["datos"] for x in listar_entidades(seccion)]


def opciones(seccion):
    entradas = lista(seccion)
    return {f"{e.get(NOMBRE[seccion], 'Sin nombre')} · {e['id']}": e["id"] for e in entradas}


def selector(seccion, etiqueta=None, key=None):
    op = opciones(seccion)
    if not op:
        st.info(f"No hay registros de {seccion.lower()} todavía.")
        return None
    texto = st.selectbox(etiqueta or f"Selecciona {seccion.lower()}", list(op), key=key)
    return op[texto]


def ejecutar(accion, *args, **kwargs):
    """Ejecuta una operación escrita y presenta error sin ocultarlo."""
    try:
        resultado = accion(*args, **kwargs)
        st.success("Operación guardada correctamente en Neo4j.")
        return resultado
    except Exception as exc:
        st.error(f"No se pudo guardar: {exc}")
        return None


def inputs(seccion, clave, valores=None):
    valores = valores or {}
    salida = {}
    campos = CAMPOS[seccion]
    a, b = st.columns(2)
    for i, (nombre, rotulo, clase) in enumerate(campos):
        contenedor = a if i % 2 == 0 else b
        with contenedor:
            anterior = valores.get(nombre)
            if clase == "area":
                salida[nombre] = st.text_area(rotulo, value=str(anterior or ""), key=f"{clave}_{nombre}", height=96)
            elif clase == "number":
                salida[nombre] = st.number_input(rotulo, min_value=0.0,
                        value=float(anterior or 0.0), step=50000.0,
                        format="%.2f", key=f"{clave}_{nombre}")
            else:
                salida[nombre] = st.text_input(rotulo, value=str(anterior or ""), key=f"{clave}_{nombre}")
    return salida


def validacion(seccion, payload):
    campo_principal = "titulo" if seccion == "Ofertas laborales" else "nombre"
    if not payload.get(campo_principal, "").strip():
        st.warning("El nombre o título no puede quedar vacío.")
        return False
    if seccion == "Usuarios" and ("@" not in payload["correo"] or "." not in payload["correo"]):
        st.warning("Escribe un correo electrónico válido.")
        return False
    return True


def pagina_crud(seccion):
    banner('Directorio profesional · Gestión de datos',seccion,
           'Consulta registros, crea entidades y mantén actualizada la información de la red.')
    repo=REPOS[seccion]
    registros=lista(seccion)
    st.markdown(f'<div class="rp-mini-stat">Registros disponibles <strong>{len(registros)}</strong> <span class="rp-muted">· Información en vivo de Neo4j</span></div>', unsafe_allow_html=True)
    consultar,crear,editar,borrar=st.tabs(['Explorar','Registrar','Editar','Eliminar'])
    with consultar:
        busqueda=st.text_input('Buscar por nombre, título o ID',key=f'buscar_{seccion}',placeholder='Escribe para filtrar...')
        filtrados=[r for r in registros if busqueda.lower() in str(r).lower()] if busqueda else registros
        st.caption(f'{len(filtrados)} resultado(s)')
        ver_tabla(filtrados)
        if seccion=='Usuarios' and registros:
            titulo_sec('Perfil profesional','Habilidades y postulaciones')
            uid=selector('Usuarios','Selecciona un profesional',key='perfil_profesional')
            if uid:
                h=habilidades_de_usuario(uid)
                p=postulaciones_de_usuario(uid)
                habilidades=''.join(f'<span class="rp-tag">{limpio(x["habilidad"])}</span>' for x in h)
                postulaciones=''.join(f'<span class="rp-tag">{limpio(x["oferta"])}</span>' for x in p)
                st.markdown('<div class="rp-result"><div class="rp-category">Competencias</div><div class="rp-tags">'+
                            (habilidades or '<span class="rp-muted">Sin habilidades vinculadas</span>')+
                            '</div><div class="rp-category" style="margin-top:18px">Postulaciones</div><div class="rp-tags">'+
                            (postulaciones or '<span class="rp-muted">Sin postulaciones</span>')+'</div></div>',unsafe_allow_html=True)
    with crear:
        st.caption('Los cambios se guardan en la base conectada. Si es compartida, utiliza esta opción con autorización del equipo.')
        with st.form(f'nuevo_{seccion}',clear_on_submit=True):
            payload=inputs(seccion,f'crear_{seccion}')
            enviado=st.form_submit_button('Crear registro',type='primary')
            if enviado and validacion(seccion,payload):
                respuesta=ejecutar(repo.crear,**payload)
                if respuesta is not None:st.rerun()
    with editar:
        if registros:
            items={f'{r.get(NOMBRE[seccion])} · {r["id"]}':r for r in registros}
            actual=st.selectbox('Selecciona el registro',list(items),key=f'edicion_{seccion}')
            registro=items[actual]
            with st.form(f'modificar_{seccion}_{registro["id"]}'):
                payload=inputs(seccion,f'editar_{seccion}_{registro["id"]}',registro)
                if st.form_submit_button('Guardar cambios',type='primary') and validacion(seccion,payload):
                    respuesta=ejecutar(repo.actualizar,registro['id'],**payload)
                    if respuesta is not None:st.rerun()
        else:st.info('Crea primero un registro.')
    with borrar:
        if registros:
            items={f'{r.get(NOMBRE[seccion])} · {r["id"]}':r['id'] for r in registros}
            etiqueta=st.selectbox('Registro que quieres eliminar',list(items),key=f'eliminar_{seccion}')
            with st.form(f'eliminar_form_{seccion}'):
                st.warning('Se eliminará el nodo y todas sus relaciones. Esta acción no se puede deshacer.')
                confirmado=st.checkbox('Comprendo y confirmo la eliminación')
                if st.form_submit_button('Eliminar registro'):
                    if not confirmado:st.warning('Marca primero la casilla de confirmación.')
                    else:
                        respuesta=ejecutar(repo.eliminar,items[etiqueta])
                        if respuesta is not None:st.rerun()
        else:st.info('No hay registros para eliminar.')


def pagina_inicio():
    banner('Panel de control · Red profesional','Job to go · Tu red, en perspectiva',
           'Profesionales, empresas y oportunidades conectadas. Conoce tu red y encuentra relaciones útiles en tiempo real.')
    totales={x['tipo']:x['total'] for x in total_entidades()}
    indicadores=[('Profesionales','Usuario','PR','#2563eb'),('Empresas','Empresa','EM','#0284c7'),
                 ('Habilidades','Habilidad','HA','#60a5fa'),('Proyectos','Proyecto','PY','#6366f1'),
                 ('Vacantes','OfertaLaboral','VA','#0891b2')]
    tarjetas_html=[]
    for etiqueta,tipo,icono,color in indicadores:
        tarjetas_html.append(f'<div class="rp-kpi" style="--kpi-accent:{color}"><div class="rp-kpi-icon">{icono}</div>'
                             f'<div class="rp-kpi-number">{int(totales.get(tipo,0)):,}</div><div class="rp-kpi-label">{etiqueta}</div></div>')
    st.markdown('<div class="rp-kpis">'+''.join(tarjetas_html)+'</div>',unsafe_allow_html=True)
    cantidad_relaciones=total_relaciones()
    st.markdown(f'<div class="rp-network">↗ <b>{cantidad_relaciones:,}</b> relaciones en la red · Datos consultados en Neo4j</div>', unsafe_allow_html=True)
    panel=PanelAnalitica()
    titulo_sec('Indicadores de la red','Habilidades requeridas y conectividad')
    c1,c2=st.columns(2,gap='large')
    with c1:
        st.markdown('**Habilidades más demandadas**')
        bloques_barras(panel.obtener_habilidades_mas_demandadas(7),'habilidad','demanda_ofertas','#2563eb')
    with c2:
        st.markdown('**Profesionales más conectados**')
        bloques_barras(panel.obtener_usuarios_mas_influyentes(7),'nombre','conexiones','#0284c7')
    titulo_sec('Vacantes recientes','Oportunidades publicadas en la red')
    ofertas_recientes = ultimas_ofertas(7)
    if ofertas_recientes:
        columnas_ofertas = st.columns(2, gap='large')
        for i, oferta in enumerate(ofertas_recientes[:4]):
            with columnas_ofertas[i % 2]:
                job_card(oferta, compact=True)
        with st.expander('Ver todas las vacantes en tabla'):
            ver_tabla(ofertas_recientes)
    else:
        st.info('Todavía no hay ofertas registradas.')
    titulo_sec('Grupos por empresa','Relaciones de empleo existentes')
    st.caption('Agrupaciones de personas vinculadas a la misma empresa; no es detección automática de comunidades mediante algoritmos.')
    ver_tabla(panel.detectar_comunidades_por_empresa(),'No existen grupos de empleados en los datos actuales.')


RELACIONES = {
    "Conectar dos profesionales": ("Usuarios", "Usuarios", Usuario().conecta_con),
    "Asignar habilidad a profesional": ("Usuarios", "Habilidades", Usuario().posee_habilidad),
    "Vincular profesional a empresa": ("Usuarios", "Empresas", Usuario().trabaja_en),
    "Asignar profesional a proyecto": ("Usuarios", "Proyectos", Usuario().participa_en),
    "Postular profesional a vacante": ("Usuarios", "Ofertas laborales", Usuario().se_postula_a),
    "Publicar oferta desde empresa": ("Empresas", "Ofertas laborales", Empresa().publica_oferta),
    "Definir habilidad requerida por oferta": ("Ofertas laborales", "Habilidades", OfertaLaboral().requiere_tener),
    "Vincular proyecto a empresa": ("Empresas", "Proyectos", Empresa().tiene_proyecto),
    "Asignar tecnología a proyecto": ("Proyectos", "Tecnologías", Proyecto().usa_tecnologia),
}


def pagina_conexiones():
    banner('Relaciones del grafo','Conectar entidades',
           'Crea vínculos profesionales y transforma registros independientes en una red de oportunidades.')
    st.markdown('<div class="rp-footnote">Una relación en Neo4j es una arista entre nodos. Ejemplo: <b>Empresa → PUBLICA → Oferta laboral</b> o <b>Usuario → POSEE → Habilidad</b>.</div>',unsafe_allow_html=True)
    titulo_sec('Crear una relación','Selecciona un tipo de conexión y sus dos extremos')
    tipo=st.selectbox('Tipo de conexión',list(RELACIONES))
    origen,destino,metodo=RELACIONES[tipo]
    a,b=st.columns(2,gap='large')
    with a:id_origen=selector(origen,f'Origen · {origen}',key='origen_rel')
    with b:id_destino=selector(destino,f'Destino · {destino}',key='destino_rel')
    if id_origen and id_destino:
        st.markdown(f'<div class="rp-mini-stat"><b>{limpio(origen)}</b> → <b>{limpio(tipo)}</b> → <b>{limpio(destino)}</b></div>',unsafe_allow_html=True)
        if id_origen==id_destino:st.warning('No puedes conectar un nodo consigo mismo.')
        elif st.button('Crear conexión',type='primary'):
            respuesta=ejecutar(metodo,id_origen,id_destino)
            if respuesta == []:st.warning('No se encontró alguno de los registros en Neo4j.')
    st.caption('Esta acción sí modifica la base de datos. En una instancia compartida, coordínala con tus compañeros.')


def pagina_empleos():
    pagina_crud("Ofertas laborales")
    st.divider()
    st.subheader("Postulación rápida")
    a, b = st.columns(2)
    with a:
        uid = selector("Usuarios", "Profesional que desea postularse", key="postula_usuario")
    with b:
        oid = selector("Ofertas laborales", "Oferta laboral", key="postula_oferta")
    if uid and oid and st.button("Enviar postulación", type="primary"):
        ejecutar(Usuario().se_postula_a, uid, oid)
    st.caption("Para definir habilidades requeridas y la empresa que publica, utiliza la sección Conexiones.")


def pagina_grafo():
    banner('Exploración visual','Mapa de conexiones',
           'Filtra, mueve y examina los nodos de la red profesional y sus relaciones.')
    c1,c2=st.columns([2.2,1],gap='large')
    with c1:tipos=st.multiselect('Tipos de nodos',list(REPOS),default=list(REPOS),key='tipos_grafo')
    with c2:limite=st.slider('Máximo de nodos',10,200,90,10)
    c3,c4=st.columns([1.1,2.3],gap='large')
    with c3:etiquetas=st.toggle('Mostrar nombres en el grafo',value=False)
    registros=datos_grafo(tipos,limite) if tipos else []
    if not registros:
        st.info('No hay nodos para los filtros seleccionados.')
        return
    colores={'Usuario':'#2563eb','Empresa':'#0284c7','Habilidad':'#60a5fa',
             'Proyecto':'#6366f1','OfertaLaboral':'#0891b2','Tecnologia':'#64748b'}
    nodos={};aristas=[]
    for r in registros:
        oid=r.get('origen_id');did=r.get('destino_id')
        if oid is not None:nodos[oid]=(r.get('origen_tipo'),r.get('origen_nombre'))
        if did is not None:nodos[did]=(r.get('destino_tipo'),r.get('destino_nombre'))
        if oid is not None and did is not None:
            aristas.append((oid,did,r.get('relacion')))
    with c4:
        opciones=['Toda la red']+[f'{nombre} · {identificador}' for identificador,(tipo,nombre) in sorted(nodos.items(),key=lambda x:str(x[1][1]))]
        foco=st.selectbox('Enfoque',opciones,key='foco_grafo')
    if foco!='Toda la red':
        fid=foco.rsplit(' · ',1)[-1]
        vecinos={fid}
        for origen,destino,_ in aristas:
            if origen==fid:vecinos.add(destino)
            if destino==fid:vecinos.add(origen)
        nodos={i:v for i,v in nodos.items() if i in vecinos}
        aristas=[x for x in aristas if x[0] in nodos and x[1] in nodos]
    net=Network(height='570px',width='100%',bgcolor='#ffffff',font_color='#1e3a5f',
                directed=True,notebook=False,cdn_resources='in_line')
    # ID único de BD como clave; etiquetas reducidas y detalle al pasar el cursor.
    for identificador,(tipo,nombre) in nodos.items():
        tipo=tipo or 'Nodo';nombre=str(nombre or identificador)
        etiqueta=nombre[:25]+('…' if len(nombre)>25 else '') if etiquetas else ''
        titulo=f'<b>{limpio(nombre)}</b><br>{limpio(tipo)} · {limpio(identificador)}'
        net.add_node(identificador,label=etiqueta,title=titulo,color=colores.get(tipo,'#93a5bc'),
                     size=24 if foco!='Toda la red' and identificador==fid else 17,
                     shape='dot',borderWidth=2,
                     font={'size':11,'face':'Arial','color':'#1d385b'})
    for origen,destino,tipo_relacion in aristas:
        pendiente = tipo_relacion in ('SOLICITA_CONEXION', 'SOLICITA_PARTICIPACION')
        net.add_edge(origen, destino,
                     title=(('Solicitud de participación pendiente' if tipo_relacion == 'SOLICITA_PARTICIPACION' else 'Solicitud de conexión pendiente') if pendiente else str(tipo_relacion or 'Relación')),
                     color=('#97a8be' if pendiente else '#9cb6d6'),
                     dashes=pendiente, width=(1.8 if pendiente else 1.35), arrows='to')
    net.set_options('{"physics":{"enabled":true,"solver":"barnesHut","barnesHut":{"gravitationalConstant":-7600,"centralGravity":0.14,"springLength":200,"springConstant":0.026,"damping":0.72},"stabilization":{"enabled":true,"iterations":180}},"interaction":{"hover":true,"navigationButtons":true,"keyboard":true,"tooltipDelay":90,"hideEdgesOnDrag":true},"edges":{"smooth":{"enabled":true,"type":"dynamic"}},"nodes":{"shadow":{"enabled":true,"size":8,"x":0,"y":3}}}')
    st.markdown(f'<div class="rp-mini-stat"><strong>{len(nodos)}</strong> nodos visibles · <strong>{len(aristas)}</strong> relaciones · Arrastra para explorar, usa la rueda para acercar y pasa el cursor para ver detalles.</div>',unsafe_allow_html=True)
    pagina=net.generate_html()
    pagina=pagina.replace('</head>','<style>body{margin:0;background:#ffffff !important;}#mynetwork{border:1px solid #dbe6f3 !important;border-radius:14px;background:#ffffff !important;}</style></head>')
    components.html(pagina,height=590,scrolling=False)
    leyenda=''.join(f'<span class="rp-legend-item" style="--dot-color:{v}"><span class="rp-dot"></span>{limpio(k)}</span>' for k,v in colores.items())
    st.markdown('<div class="rp-legend">'+leyenda+'</div>',unsafe_allow_html=True)
    st.caption('Las líneas discontinuas son solicitudes pendientes. CONECTA_CON es una conexión aceptada; PARTICIPA_EN confirma la participación en un proyecto. Los filtros no modifican Neo4j.')


def pagina_recomendaciones():
    banner('Recomendaciones inteligentes','Descubrir oportunidades',
           'Sugerencias explicables calculadas a partir de las habilidades y relaciones almacenadas en el grafo.')
    st.markdown('<div class="rp-footnote">Estas recomendaciones utilizan reglas y consultas Cypher sobre Neo4j, no un modelo de inteligencia artificial entrenado.</div>',unsafe_allow_html=True)
    contacto,empleo,colaborador,candidato=st.tabs(['Contactos','Empleos','Colaboradores','Candidatos'])
    motor=SistemaRecomendacion()
    with contacto:
        st.markdown('**Personas que podrías conocer**')
        uid=selector('Usuarios','Selecciona un profesional',key='reco_contacto')
        if uid:
            datos=motor.recomendar_contactos(uid)
            tarjetas(datos,'Contacto sugerido','nombre',[('Correo','correo')],score_key='amigos_en_comun',score_label='contactos en común')
    with empleo:
        st.markdown('**Vacantes que coinciden con tus habilidades**')
        uid=selector('Usuarios','Selecciona un profesional',key='reco_empleo')
        if uid:
            datos=motor.recomendar_empleos(uid)
            tarjetas(datos,'Oportunidad laboral','titulo_oferta',[('Empresa','empresa'),('Salario (COP)','salario')],
                     score_key='habilidades_coincidentes',lista_key='habilidades_match')
    with colaborador:
        st.markdown('**Profesionales afines al proyecto**')
        pid=selector('Proyectos','Selecciona un proyecto',key='reco_colab')
        if pid:
            datos=motor.recomendar_colaboradores_para_proyecto(pid)
            tarjetas(datos,'Posible colaborador','nombre',[('Experiencia','experiencia'),('Habilidades afines','habilidades_afines')],
                     score_key='puntaje_relevancia',score_label='puntos')
            if any((x.get('puntaje_relevancia') or 0)==0 for x in datos):
                st.caption('Un puntaje 0 indica que la consulta no identificó afinidad por los criterios evaluados.')
    with candidato:
        st.markdown('**Candidatos para la vacante**')
        oid=selector('Ofertas laborales','Selecciona una oferta',key='reco_cand')
        if oid:
            datos=ConsultasGrafo().candidatos_recomendados(oid)
            tarjetas(datos,'Candidato potencial','candidato',[('Oferta','oferta'),('Empresa','empresa'),
                     ('Distancia en red','distancia_red')],score_key='competencias_coincidentes',lista_key='habilidades_coincidentes')


def pintar_camino(resultado):
    if not resultado:
        st.info('No se encontró un camino entre las entidades seleccionadas dentro del límite de saltos de la consulta.')
        return
    pasos=resultado.get('recorrido') or resultado.get('camino') or []
    if not pasos:
        st.info('La consulta no devolvió nodos para representar.')
        with st.expander('Resultado técnico · JSON'):st.json(resultado)
        return
    relaciones=resultado.get('relaciones') or []
    partes=[]
    for i,n in enumerate(pasos):
        tipo=str(n.get('tipo') or n.get('label') or 'Nodo')
        nombre=str(n.get('nombre') or n.get('id') or 'Sin nombre')
        partes.append(f'<div class="rp-path-node"><div class="rp-path-kind">{limpio(iconos(tipo))}</div>'
                      f'<div class="rp-path-name">{limpio(nombre)}</div></div>')
        if i<len(pasos)-1:
            relacion=limpio(relaciones[i]) if i<len(relaciones) else 'Conexión'
            partes.append(f'<div class="rp-path-arrow"><b>→</b><small>{relacion}</small></div>')
    st.markdown(f'<div class="rp-mini-stat"><strong>{len(pasos)-1}</strong> relaciones · <strong>{len(pasos)}</strong> nodos en el recorrido encontrado</div>',unsafe_allow_html=True)
    titulo_sec('Recorrido visual','Ruta obtenida de Neo4j')
    st.markdown('<div class="rp-path">'+''.join(partes)+'</div>',unsafe_allow_html=True)
    with st.expander('Ver detalle técnico · JSON'):
        st.json(resultado)


def pagina_consultas():
    banner("Consultas Cypher", "Análisis de la red",
           "Responde las preguntas del enunciado mediante recorridos y patrones entre nodos.")
    modo = st.selectbox("¿Qué quieres investigar?", [
        "Profesionales con habilidades similares",
        "Contactos en común entre profesionales",
        "Ruta más corta: usuario → empresa",
        "Camino entre dos profesionales",
        "Ruta: profesional → vacante",
        "Proyectos relacionados",
    ])
    explicaciones={
        'Profesionales con habilidades similares':'Compara pares de personas conectadas a las mismas habilidades.',
        'Contactos en común entre profesionales':'Busca profesionales conectados a dos personas simultáneamente.',
        'Ruta más corta: usuario → empresa':'Encuentra la ruta con menor número de relaciones entre el profesional y la empresa.',
        'Camino entre dos profesionales':'Recorre conexiones profesionales hasta hallar el camino más corto disponible.',
        'Ruta: profesional → vacante':'Explora cómo un profesional se vincula con una oferta mediante las relaciones del grafo.',
        'Proyectos relacionados':'Detecta tecnologías compartidas, miembros comunes y profesionales conectados entre proyectos.'
    }
    st.markdown('<div class="rp-footnote">'+limpio(explicaciones[modo])+'</div>',unsafe_allow_html=True)
    motor = ConsultasGrafo()
    caminos = CaminosYConexiones()
    if modo == "Profesionales con habilidades similares":
        minimo = st.number_input("Mínimo de habilidades compartidas", 1, 10, 1)
        ver_tabla(motor.usuarios_con_habilidades_similares(minimo), "No hay pares de usuarios con esas habilidades en común.")
    elif modo == "Proyectos relacionados":
        ver_tabla(motor.proyectos_relacionados(), "No se encontraron proyectos con coincidencias.")
    elif modo in ("Contactos en común entre profesionales", "Camino entre dos profesionales"):
        x, y = st.columns(2)
        with x:
            u1 = selector("Usuarios", "Primer profesional", key="consulta_u1")
        with y:
            u2 = selector("Usuarios", "Segundo profesional", key="consulta_u2")
        if u1 and u2 and u1 != u2:
            if modo.startswith("Contactos"):
                ver_tabla(motor.contactos_en_comun(u1, u2), "No hay contactos en común.")
            else:
                r = caminos.consultar_camino_entre_usuarios(u1, u2)
                pintar_camino(r[0] if r else None)
        elif u1 and u2:
            st.info("Selecciona dos personas diferentes.")
    elif modo == "Ruta más corta: usuario → empresa":
        x, y = st.columns(2)
        with x:
            u = selector("Usuarios", "Profesional", key="ruta_empresa_u")
        with y:
            e = selector("Empresas", "Empresa", key="ruta_empresa_e")
        if u and e:
            pintar_camino(motor.ruta_mas_corta_usuario_empresa(u, e))
    elif modo == "Ruta: profesional → vacante":
        x, y = st.columns(2)
        with x:
            u = selector("Usuarios", "Profesional", key="ruta_oferta_u")
        with y:
            o = selector("Ofertas laborales", "Oferta", key="ruta_oferta_o")
        if u and o:
            r = caminos.consultar_camino_usuario_a_oferta(u, o)
            pintar_camino(r[0] if r else None)



# ───────────────────────────────────────────────────────────────────
# ACCESO DE DEMOSTRACIÓN (sin contraseñas nuevas ni entidades Cuenta)
# Profesional: correo como usuario y clave; empresa: nombre como usuario y clave.
# Administrador: credenciales privadas existentes de .env.
# ATENCIÓN: Este acceso no es seguro; únicamente sirve para una demo local.

def leer_datos(query, params=None):
    return db.ejecutar_consulta(query, params or {}, write=False)


def iniciar_sesion_admin(usuario, clave):
    esperado = os.getenv('JOBTOGO_ADMIN_USER', '').strip()
    secreto = os.getenv('JOBTOGO_ADMIN_PASSWORD', '')
    if not (esperado and secreto and usuario and clave):
        return None
    if hmac.compare_digest(usuario, esperado) and hmac.compare_digest(clave, secreto):
        return {'rol': 'admin', 'id': None, 'nombre': 'Administrador'}
    return None


def autenticar_cuenta(identificador, clave, rol):
    """Acceso simple con propiedades existentes; sin almacenar contraseñas."""
    if rol not in ('profesional', 'empresa'):
        return None
    usuario = (identificador or '').strip()
    contrasena = (clave or '').strip()
    if not usuario or not contrasena or usuario.casefold() != contrasena.casefold():
        return None
    if rol == 'profesional':
        filas = leer_datos('''
            MATCH (u:Usuario)
            WHERE toLower(trim(u.correo)) = toLower($dato)
            RETURN u.id AS id, u.nombre AS nombre
            LIMIT 2
        ''', {'dato': usuario})
    else:
        filas = leer_datos('''
            MATCH (e:Empresa)
            WHERE toLower(trim(e.nombre)) = toLower($dato)
            RETURN e.id AS id, e.nombre AS nombre
            LIMIT 2
        ''', {'dato': usuario})
    # Evitar elegir una cuenta arbitraria si existen identificadores duplicados.
    if len(filas) != 1:
        return None
    perfil = filas[0]
    return {'rol': rol, 'id': perfil['id'], 'nombre': perfil['nombre']}


def abrir_sesion(sesion):
    st.session_state['jtg_auth'] = sesion
    st.session_state['pagina_actual'] = 'Inicio'
    st.rerun()


def registrar_desde_formulario(rol, datos, habilidades_ids=None):
    """Registra perfiles existentes y, si corresponde, sus habilidades iniciales."""
    try:
        if rol == 'profesional':
            correo = (datos.get('correo') or '').strip()
            if '@' not in correo or '.' not in correo.rsplit('@', 1)[-1]:
                st.error('Escribe un correo electrónico válido.')
                return
            # Validar las habilidades antes de insertar el nuevo Usuario.
            ids_seleccionados = list(dict.fromkeys(habilidades_ids or []))
            catalogo_actual = {h['id'] for h in habilidades_catalogo()}
            if not set(ids_seleccionados).issubset(catalogo_actual):
                st.error('El catálogo de habilidades cambió. Actualiza la página.')
                return
        if not (datos.get('nombre') or '').strip():
            st.error('Escribe el nombre del perfil.')
            return
        id_nuevo = crear_perfil(rol, datos)
        if rol == 'profesional' and ids_seleccionados:
            try:
                actualizar_habilidades_profesional(id_nuevo, ids_seleccionados)
            except Exception:
                # Solo se elimina el nodo recién creado si falla su inicialización.
                revertir_perfil_nuevo('profesional', id_nuevo)
                raise
        abrir_sesion({'rol': rol, 'id': id_nuevo, 'nombre': datos['nombre']})
    except (ValueError, KeyError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error('No se pudo crear el perfil. Revisa la conexión y los permisos de escritura en Neo4j.')
        with st.expander('Detalle técnico'):
            st.exception(exc)


def pantalla_login():
    # Acceso académico: diseño claro y formularios originales preservados.
    st.markdown('''<style>
      [data-testid="stSidebar"]{display:none !important}
      [data-testid="stSidebarCollapsedControl"]{display:none !important}
      .block-container {max-width:1180px !important;padding-top:4vh !important;}
    </style>''', unsafe_allow_html=True)
    st.markdown('''<div class="jt-logo-line"><div class="jt-logo-mark">J</div>
      <div class="jt-logo-wordmark">Job to go</div></div>
      <div class="jt-logo-subtitle">Tu red profesional, en un solo lugar.</div>''',
      unsafe_allow_html=True)
    izquierda, derecha = st.columns([0.9, 1.1], gap='large')
    with izquierda:
        st.markdown('''<div class="jt-auth-promo">
          <span class="jt-auth-kicker">PLATAFORMA PROFESIONAL</span>
          <h2>El siguiente paso de tu carrera empieza aquí.</h2>
          <p>Encuentra vacantes, crea conexiones y participa en proyectos.
          Todo en una plataforma donde cada relación abre oportunidades.</p>
          <div class="jt-auth-divider"></div>
          <div class="jt-auth-point"><span>1</span> Conecta con profesionales</div>
          <div class="jt-auth-point"><span>2</span> Descubre ofertas compatibles</div>
          <div class="jt-auth-point"><span>3</span> Encuentra proyectos y talento</div>
        </div>''', unsafe_allow_html=True)
    with derecha:
        st.markdown('### Bienvenido a Job to go')
        st.caption('Inicia sesión o crea tu perfil profesional o empresarial.')
        entrar, registrarse = st.tabs(['Iniciar sesión', 'Crear cuenta'])
        with entrar:
            rol_visible = st.radio('Tipo de acceso', ['Profesional', 'Empresa', 'Administrador'],
                                  horizontal=True, key='jtg_tipo_entrar')
            rol = {'Profesional': 'profesional', 'Empresa': 'empresa', 'Administrador': 'admin'}[rol_visible]
            with st.form(f'jtg_login_{rol}'):
                campo = {'profesional': 'Correo electrónico', 'empresa': 'Nombre de la empresa',
                         'admin': 'Usuario administrador'}[rol]
                identificador = st.text_input(campo, key=f'jtg_identificador_{rol}')
                clave = st.text_input('Contraseña', type='password', key=f'jtg_clave_{rol}')
                if st.form_submit_button('Ingresar', type='primary', use_container_width=True):
                    try:
                        sesion = (iniciar_sesion_admin(identificador, clave) if rol == 'admin'
                                  else autenticar_cuenta(identificador, clave, rol))
                    except Exception as exc:
                        st.error(f'No fue posible consultar el perfil en Neo4j: {exc}')
                    else:
                        if sesion:
                            abrir_sesion(sesion)
                        else:
                            st.error('No se encontró el perfil o los datos ingresados no coinciden.')
        with registrarse:
            tipo_nuevo = st.radio('Quiero registrarme como', ['Profesional', 'Empresa'],
                                 horizontal=True, key='jtg_tipo_registro')
            if tipo_nuevo == 'Profesional':
                with st.form('jtg_registro_profesional'):
                    nombre = st.text_input('Nombre completo')
                    correo = st.text_input('Correo electrónico')
                    col1, col2 = st.columns(2)
                    with col1:
                        telefono = st.text_input('Teléfono')
                        ubicacion = st.text_input('Ciudad / ubicación')
                    with col2:
                        educacion = st.text_input('Educación')
                        experiencia = st.text_area('Experiencia', height=95)
                    habilidades_opts = {
                        f'{h["nombre"]} · {h["id"]}': h['id'] for h in habilidades_catalogo()
                    }
                    seleccion_habilidades = st.multiselect('Mis habilidades', list(habilidades_opts))
                    if st.form_submit_button('Crear perfil profesional', type='primary', use_container_width=True):
                        registrar_desde_formulario('profesional', {
                            'nombre': nombre.strip(), 'correo': correo.strip(),
                            'telefono': telefono.strip(), 'ubicacion': ubicacion.strip(),
                            'experiencia': experiencia.strip(), 'educacion': educacion.strip(),
                        }, [habilidades_opts[h] for h in seleccion_habilidades])
            else:
                with st.form('jtg_registro_empresa'):
                    nombre = st.text_input('Nombre de la empresa')
                    col1, col2 = st.columns(2)
                    with col1:
                        industria = st.text_input('Sector / industria')
                        ubicacion = st.text_input('Ciudad / ubicación')
                    with col2:
                        tamano = st.text_input('Tamaño de la empresa')
                        descripcion = st.text_area('Descripción de la empresa', height=95)
                    if st.form_submit_button('Crear perfil empresarial', type='primary', use_container_width=True):
                        registrar_desde_formulario('empresa', {
                            'nombre': nombre.strip(), 'industria': industria.strip(),
                            'ubicacion': ubicacion.strip(), 'tamano': tamano.strip(),
                            'descripcion': descripcion.strip(),
                        })


def perfil_por_id(tipo, id_registro):
    etiqueta = 'Usuario' if tipo == 'profesional' else 'Empresa'
    filas = leer_datos(f'MATCH (n:{etiqueta} {{id: $id}}) RETURN properties(n) AS perfil', {'id': id_registro})
    return filas[0]['perfil'] if filas else None


def ficha_perfil(perfil, campos):
    if not perfil:
        st.error('Este perfil ya no se encuentra en la base de datos.')
        return
    portrait_card(perfil.get('nombre') or 'Perfil',
                  category='Organización' if 'industria' in perfil else 'Profesional',
                  location=perfil.get('ubicacion') or '',
                  description=perfil.get('descripcion') or perfil.get('experiencia') or '',
                  detail=perfil.get('industria') or perfil.get('educacion') or '')
    filas = []
    for clave, etiqueta in campos:
        val = perfil.get(clave)
        if val is None or val == '':
            continue
        if clave in ('experiencia','descripcion'):  # Ya se presenta arriba en la tarjeta.
            continue
        filas.append(f'<div class="jt-profile-detail"><span>{limpio(etiqueta)}</span><strong>{limpio(val)}</strong></div>')
    if filas:
        st.markdown('<div class="jt-profile-details">'+''.join(filas)+'</div>',unsafe_allow_html=True)


def ofertas_empresa(empresa_id):
    return leer_datos('''
        MATCH (e:Empresa {id:$id})-[:PUBLICA]->(o:OfertaLaboral)
        RETURN properties(o) AS datos ORDER BY o.titulo
    ''', {'id': empresa_id})


def notificar_red(texto):
    """Conserva el resultado de una acción después del refresco de Streamlit."""
    st.session_state['jtg_red_mensaje'] = texto
    st.rerun()


def tarjeta_persona(persona, subtitulo='Profesional'):
    portrait_card(persona.get('nombre') or 'Profesional', category=subtitulo,
                  location=persona.get('ubicacion') or 'Ubicación no registrada',
                  description=str(persona.get('experiencia') or '')[:185])


def pagina_mi_red(usuario_id):
    banner('Red profesional', 'Conecta con profesionales',
           'Envía invitaciones, responde solicitudes y construye tu red de contactos.')
    recibidas = solicitudes_recibidas(usuario_id)
    enviadas = solicitudes_enviadas(usuario_id)
    contactos = contactos_de_profesional(usuario_id)
    disponibles = profesionales_para_conectar(usuario_id)
    cols = st.columns(3)
    cols[0].metric('Mis conexiones', len(contactos))
    cols[1].metric('Solicitudes recibidas', len(recibidas))
    cols[2].metric('Solicitudes enviadas', len(enviadas))
    mensaje = st.session_state.pop('jtg_red_mensaje', None)
    if mensaje:
        st.success(mensaje)
    explorar, bandeja, pendientes, conectados = st.tabs([
        'Descubrir personas', f'Recibidas ({len(recibidas)})',
        f'Enviadas ({len(enviadas)})', f'Mis conexiones ({len(contactos)})'
    ])
    with explorar:
        st.caption('Solo se muestran personas con las que todavía no tienes una conexión ni una solicitud pendiente.')
        busqueda = st.text_input('Buscar profesionales', key='jtg_buscar_profesionales',
                                 placeholder='Nombre, ubicación o experiencia')
        visibles = [p for p in disponibles if busqueda.casefold() in
                    ' '.join(str(p.get(k) or '') for k in ('nombre', 'ubicacion', 'experiencia')).casefold()]
        if not visibles:
            st.info('No hay más profesionales disponibles con ese filtro.')
        for p in visibles:
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                tarjeta_persona(p)
            with col_btn:
                if st.button('Conectar', key=f'jtg_enviar_{p["id"]}',
                             use_container_width=True, type='primary'):
                    try:
                        solicitar_conexion(usuario_id, p['id'])
                        notificar_red(f'Solicitud enviada a {p["nombre"]}.')
                    except Exception as exc:
                        st.error(f'No se pudo enviar la solicitud: {exc}')
    with bandeja:
        st.caption('Acepta o rechaza solicitudes dirigidas a tu perfil.')
        if not recibidas:
            st.info('No tienes solicitudes de conexión pendientes.')
        for p in recibidas:
            col_info, col_si, col_no = st.columns([4, 1, 1])
            with col_info:
                tarjeta_persona(p, 'Quiere conectar contigo')
            with col_si:
                if st.button('Aceptar', key=f'jtg_aceptar_{p["id"]}',
                             use_container_width=True, type='primary'):
                    try:
                        aceptar_solicitud(usuario_id, p['id'])
                        notificar_red(f'Ahora estás conectado con {p["nombre"]}.')
                    except Exception as exc:
                        st.error(f'No se pudo aceptar: {exc}')
            with col_no:
                if st.button('Rechazar', key=f'jtg_rechazar_{p["id"]}',
                             use_container_width=True):
                    try:
                        rechazar_solicitud(usuario_id, p['id'])
                        notificar_red(f'Solicitud de {p["nombre"]} rechazada.')
                    except Exception as exc:
                        st.error(f'No se pudo rechazar: {exc}')
    with pendientes:
        if not enviadas:
            st.info('No tienes solicitudes enviadas pendientes de respuesta.')
        for p in enviadas:
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                tarjeta_persona(p, 'Esperando respuesta')
            with col_btn:
                if st.button('Cancelar', key=f'jtg_cancelar_{p["id"]}', use_container_width=True):
                    try:
                        cancelar_solicitud(usuario_id, p['id'])
                        notificar_red(f'Solicitud a {p["nombre"]} cancelada.')
                    except Exception as exc:
                        st.error(f'No se pudo cancelar: {exc}')
    with conectados:
        if not contactos:
            st.info('Aún no tienes conexiones aceptadas. Descubre personas y envíales una solicitud.')
        for p in contactos:
            tarjeta_persona(p, 'Conexión profesional')



def mostrar_empresa_del_profesional(usuario_id):
    """Muestra información laboral utilizando la relación TRABAJA_EN existente."""
    empresas = empresas_de_profesional(usuario_id)
    titulo_sec('Mi empresa', 'Vinculación laboral registrada en Neo4j')
    if not empresas:
        st.info('Todavía no tienes una empresa vinculada a tu perfil. El administrador puede registrar la relación desde Conexiones.')
        return
    for e in empresas:
        st.markdown(
            '<div class="rp-result" style="margin-bottom:10px">'
            '<div class="rp-category">Empresa donde trabajas</div>'
            f'<h4>{limpio(e.get("nombre") or "Empresa")}</h4>'
            f'<p>{limpio(e.get("industria") or "Industria no indicada")} · '
            f'{limpio(e.get("ubicacion") or "Ubicación no indicada")}</p>'
            f'<p>Proyectos publicados: {int(e.get("total_proyectos") or 0)}</p>'
            '</div>', unsafe_allow_html=True,
        )
    if st.button('Ver proyectos de mi empresa', key='jtg_ir_proyectos_perfil', type='primary'):
        st.session_state['pagina_actual'] = 'Proyectos de mi empresa'
        st.rerun()


def pagina_proyectos_profesional(usuario_id):
    banner('Participación profesional', 'Proyectos de mi empresa',
           'Explora los proyectos de tu empresa y solicita participar. La empresa decide si acepta tu solicitud.')
    empresas = empresas_de_profesional(usuario_id)
    proyectos = proyectos_para_profesional(usuario_id) if empresas else []
    participando = participaciones_de_profesional(usuario_id)
    cols = st.columns(3)
    cols[0].metric('Empresas vinculadas', len(empresas))
    cols[1].metric('Proyectos disponibles', sum(p['estado'] == 'Disponible' for p in proyectos))
    cols[2].metric('Solicitudes pendientes', sum(p['estado'] == 'Pendiente' for p in proyectos))
    mensaje = st.session_state.pop('jtg_proyecto_mensaje', None)
    if mensaje:
        st.success(mensaje)
    if not empresas:
        st.info('Tu perfil no tiene una empresa asociada. Para solicitar un proyecto, primero debe existir una relación TRABAJA_EN con esa empresa.')
    elif not proyectos:
        st.info('Tu empresa aún no ha publicado proyectos. Vuelve a consultar cuando tenga proyectos disponibles.')
    else:
        st.caption('Solo puedes solicitar proyectos de las empresas donde figuras como empleado.')
        for proyecto in proyectos:
            estado = proyecto.get('estado') or 'Disponible'
            detalles = ', '.join(proyecto.get('tecnologias') or []) or 'No especificadas'
            col_info, col_accion = st.columns([4, 1], gap='medium')
            with col_info:
                st.markdown(
                    '<div class="rp-result" style="margin-bottom:10px">'
                    f'<div class="rp-category">{limpio(proyecto.get("empresa") or "Empresa")}</div>'
                    f'<h4>{limpio(proyecto.get("nombre") or "Proyecto")}</h4>'
                    f'<p>{limpio(proyecto.get("descripcion") or "Sin descripción")}</p>'
                    f'<p><b>Tecnologías:</b> {limpio(detalles)}</p>'
                    f'<div class="rp-tags"><span class="rp-tag">{limpio(estado)}</span></div>'
                    '</div>', unsafe_allow_html=True,
                )
            with col_accion:
                if estado == 'Disponible':
                    if st.button('Solicitar ingreso', key=f'jtg_solicitar_proy_{proyecto["id"]}_{proyecto["empresa_id"]}',
                                 type='primary', use_container_width=True):
                        try:
                            solicitar_participacion_proyecto(usuario_id, proyecto['id'])
                            st.session_state['jtg_proyecto_mensaje'] = 'Solicitud enviada a la empresa. Está pendiente de aprobación.'
                            st.rerun()
                        except Exception as exc:
                            st.error(f'No se pudo solicitar: {exc}')
                elif estado == 'Pendiente':
                    st.caption('Pendiente de revisión')
                    if st.button('Cancelar solicitud', key=f'jtg_cancelar_proy_{proyecto["id"]}_{proyecto["empresa_id"]}', use_container_width=True):
                        try:
                            cancelar_participacion_proyecto(usuario_id, proyecto['id'])
                            st.session_state['jtg_proyecto_mensaje'] = 'Solicitud cancelada.'
                            st.rerun()
                        except Exception as exc:
                            st.error(f'No se pudo cancelar: {exc}')
                else:
                    st.success('Ya participas')
    titulo_sec('Mis participaciones', 'Proyectos en los que ya eres integrante')
    ver_tabla(participando, 'Aún no participas en ningún proyecto.')


def pagina_profesional(auth, seccion):
    usuario_id = auth['id']
    perfil = perfil_por_id('profesional', usuario_id)
    if not perfil:
        st.error('Este perfil ya no existe. Contacta al administrador.')
        return
    if seccion == 'Inicio':
        banner('Mi espacio · Profesional',f'Bienvenido, {perfil.get("nombre", "profesional")}',
               'Encuentra vacantes compatibles, consulta tus postulaciones y amplía tu red.')
        habilidades = habilidades_de_usuario(usuario_id)
        postulaciones = consultar_postulaciones(usuario_id)
        ofertas = SistemaRecomendacion().recomendar_empleos(usuario_id)
        x,y,z = st.columns(3)
        x.metric('Mis habilidades', len(habilidades))
        y.metric('Mis postulaciones', len(postulaciones))
        z.metric('Ofertas recomendadas', len(ofertas))
        titulo_sec('Ofertas para ti', 'Coincidencias calculadas a partir de tus habilidades')
        if ofertas:
            for oferta in ofertas[:4]:
                job_card(oferta, recommended=True, compact=True)
        else:
            st.info('Todavía no hay ofertas recomendadas para tu perfil.')
        if st.button('Ver todas las vacantes',type='primary'):
            st.session_state['pagina_actual']='Buscar empleos'
            st.rerun()
        mostrar_empresa_del_profesional(usuario_id)
        st.caption('Accede a Empleos guardados, Mis postulaciones y Notificaciones desde el menú lateral.')
    elif seccion == 'Mi perfil':
        banner('Espacio profesional','Mi perfil','Consulta y actualiza tu información profesional.')
        ficha_perfil(perfil,[('nombre','Nombre'),('correo','Correo'),('telefono','Teléfono'),
                             ('ubicacion','Ubicación'),('experiencia','Experiencia'),('educacion','Educación')])
        progreso_perfil(perfil, len(habilidades_de_usuario(usuario_id)))
        mostrar_empresa_del_profesional(usuario_id)
        titulo_sec('Mis habilidades', 'Puedes agregarlas o quitarlas desde tu propio perfil')
        habilidades = habilidades_de_usuario(usuario_id)
        st.write(', '.join(h['habilidad'] for h in habilidades) if habilidades else 'Sin habilidades asignadas.')
        catalogo = habilidades_catalogo()
        opciones_habilidades = {f'{h["nombre"]} · {h["id"]}': h['id'] for h in catalogo}
        actuales = set(ids_habilidades_usuario(usuario_id))
        with st.form('jtg_mis_habilidades'):
            seleccion = st.multiselect(
                'Selecciona tus habilidades', list(opciones_habilidades),
                default=[nombre for nombre, id_h in opciones_habilidades.items() if id_h in actuales],
                help='Estas habilidades se vinculan a tu perfil en Neo4j mediante POSEE.'
            )
            if st.form_submit_button('Guardar mis habilidades', type='primary'):
                try:
                    resultado = actualizar_habilidades_profesional(
                        usuario_id, [opciones_habilidades[h] for h in seleccion]
                    )
                    if resultado:
                        st.success('Habilidades actualizadas.')
                        st.rerun()
                except Exception as exc:
                    st.error(f'No se pudieron actualizar tus habilidades: {exc}')
        with st.expander('Editar mi perfil'):
            with st.form('jtg_editar_perfil_profesional'):
                nombre = st.text_input('Nombre completo',value=perfil.get('nombre',''))
                telefono = st.text_input('Teléfono',value=perfil.get('telefono',''))
                ubicacion = st.text_input('Ubicación',value=perfil.get('ubicacion',''))
                experiencia = st.text_area('Experiencia',value=perfil.get('experiencia',''))
                educacion = st.text_area('Educación',value=perfil.get('educacion',''))
                if st.form_submit_button('Guardar cambios',type='primary'):
                    if not nombre.strip():
                        st.error('El nombre no puede quedar vacío.')
                    else:
                        try:
                            resultado = actualizar_profesional(usuario_id,{
                                'nombre':nombre.strip(),'telefono':telefono.strip(),
                                'ubicacion':ubicacion.strip(),'experiencia':experiencia.strip(),
                                'educacion':educacion.strip()})
                            if resultado:
                                st.session_state['jtg_auth']['nombre']=nombre.strip()
                                st.success('Perfil actualizado.')
                                st.rerun()
                            else:st.error('El usuario ya no existe.')
                        except Exception as exc:st.error(f'No se pudo guardar: {exc}')
    elif seccion == 'Buscar empleos':
        pagina_busqueda(usuario_id)
    elif seccion == 'Empleos guardados':
        pagina_favoritos(usuario_id)
    elif seccion == 'Mis postulaciones':
        pagina_postulaciones(usuario_id)
    elif seccion == 'Mi empresa laboral':
        pagina_empresa_laboral(usuario_id, empresas_de_profesional(usuario_id))
    elif seccion == 'Notificaciones':
        pagina_centro_notificaciones('profesional', usuario_id)
    elif seccion == 'Recomendaciones':
        banner('Tu red profesional','Recomendaciones para ti','Sugerencias basadas en el grafo de Neo4j.')
        a,b=st.tabs(['Empleos compatibles','Contactos sugeridos'])
        with a:
            datos=SistemaRecomendacion().recomendar_empleos(usuario_id)
            tarjetas(datos,'Oportunidad laboral','titulo_oferta',
                     [('Empresa','empresa'),('Salario','salario')],
                     score_key='habilidades_coincidentes',lista_key='habilidades_match')
            if st.button('Buscar vacantes para postularme'):
                st.session_state['pagina_actual']='Buscar empleos'
                st.rerun()
        with b:
            datos=SistemaRecomendacion().recomendar_contactos(usuario_id)
            tarjetas(datos,'Contacto sugerido','nombre',[],
                     score_key='amigos_en_comun',score_label='contactos en común')
            if st.button('Enviar solicitudes de conexión', key='jtg_desde_recomendaciones'):
                st.session_state['pagina_actual'] = 'Mi red'
                st.rerun()
    elif seccion == 'Mi red':
        pagina_mi_red(usuario_id)
    elif seccion == 'Proyectos de mi empresa':
        pagina_proyectos_profesional(usuario_id)


def pagina_proyectos_empresa(empresa_id):
    banner('Gestión empresarial', 'Mis proyectos',
           'Crea y administra proyectos vinculados a tu empresa y a sus tecnologías.')
    proyectos = proyectos_de_empresa(empresa_id)
    titulo_sec('Proyectos registrados', 'Solo proyectos asociados a esta empresa')
    ver_tabla(proyectos, 'Todavía no hay proyectos asociados a tu empresa.')

    st.divider()
    solicitudes = solicitudes_proyectos_empresa(empresa_id)
    participantes = participantes_proyectos_empresa(empresa_id)
    titulo_sec('Solicitudes de participación', 'Acepta o rechaza empleados que quieren unirse a tus proyectos')
    st.metric('Solicitudes pendientes', len(solicitudes))
    mensaje = st.session_state.pop('jtg_empresa_proyecto_mensaje', None)
    if mensaje:
        st.success(mensaje)
    if not solicitudes:
        st.info('No hay solicitudes pendientes para tus proyectos.')
    for solicitud in solicitudes:
        col_info, col_aceptar, col_rechazar = st.columns([4, 1, 1], gap='small')
        with col_info:
            st.markdown(
                '<div class="rp-result" style="margin-bottom:10px">'
                f'<div class="rp-category">{limpio(solicitud.get("proyecto") or "Proyecto")}</div>'
                f'<h4>{limpio(solicitud.get("profesional") or "Profesional")}</h4>'
                f'<p>{limpio(solicitud.get("correo") or "Sin correo")}</p>'
                + ('<p>Este profesional ya no figura como empleado; solo puedes rechazar la solicitud.</p>'
                   if not solicitud.get('es_empleado') else '') +
                '</div>', unsafe_allow_html=True,
            )
        with col_aceptar:
            if st.button('Aceptar', key=f'jtg_aceptar_proy_{solicitud["proyecto_id"]}_{solicitud["usuario_id"]}',
                         type='primary', use_container_width=True,
                         disabled=not solicitud.get('es_empleado')):
                try:
                    aceptar_participacion_proyecto(empresa_id, solicitud['usuario_id'], solicitud['proyecto_id'])
                    st.session_state['jtg_empresa_proyecto_mensaje'] = 'Solicitud aceptada. El profesional ya participa en el proyecto.'
                    st.rerun()
                except Exception as exc:
                    st.error(f'No se pudo aceptar: {exc}')
        with col_rechazar:
            if st.button('Rechazar', key=f'jtg_rechazar_proy_{solicitud["proyecto_id"]}_{solicitud["usuario_id"]}',
                         use_container_width=True):
                try:
                    rechazar_participacion_proyecto(empresa_id, solicitud['usuario_id'], solicitud['proyecto_id'])
                    st.session_state['jtg_empresa_proyecto_mensaje'] = 'Solicitud rechazada.'
                    st.rerun()
                except Exception as exc:
                    st.error(f'No se pudo rechazar: {exc}')
    titulo_sec('Integrantes de mis proyectos', 'Participaciones registradas en el grafo')
    ver_tabla(participantes, 'Todavía no hay integrantes vinculados a estos proyectos.')


    titulo_sec('Crear un proyecto', 'El proyecto quedará vinculado a tu empresa')
    tecnologias = tecnologias_catalogo()
    opciones_tecnologias = {f'{t["nombre"]} · {t["id"]}':t['id'] for t in tecnologias}
    with st.form('jtg_crear_proyecto_empresa', clear_on_submit=True):
        nombre = st.text_input('Nombre del proyecto')
        descripcion = st.text_area('Descripción del proyecto')
        col1, col2 = st.columns(2)
        with col1:
            inicio = st.date_input('Fecha de inicio', value=date.today())
        with col2:
            fin = st.date_input('Fecha de finalización', value=date.today()+timedelta(days=90))
        elegidas = st.multiselect('Tecnologías utilizadas', list(opciones_tecnologias),
                                   help='Opcional: selecciona tecnologías ya registradas en Neo4j.')
        if st.form_submit_button('Crear proyecto', type='primary', use_container_width=True):
            if not nombre.strip():
                st.error('El proyecto necesita un nombre.')
            elif fin < inicio:
                st.error('La fecha final no puede ser anterior a la inicial.')
            else:
                try:
                    creado = crear_proyecto_empresa(empresa_id, {
                        'nombre': nombre.strip(), 'descripcion': descripcion.strip(),
                        'fecha_inicio':inicio.isoformat(), 'fecha_fin':fin.isoformat(),
                    }, [opciones_tecnologias[t] for t in elegidas])
                    st.toast(f'Proyecto registrado: {creado}')
                    st.rerun()
                except Exception as exc:
                    st.error(f'No se pudo crear el proyecto: {exc}')

    if proyectos:
        with st.expander('Editar un proyecto existente'):
            opciones_proyecto = {f'{p["nombre"]} · {p["id"]}':p for p in proyectos}
            elegido = st.selectbox('Proyecto a editar', list(opciones_proyecto), key='jtg_empresa_proyecto_editar')
            actual = opciones_proyecto[elegido]
            with st.form(f'jtg_form_proyecto_{actual["id"]}'):
                nuevo_nombre = st.text_input('Nombre', value=actual.get('nombre') or '')
                nueva_descripcion = st.text_area('Descripción', value=actual.get('descripcion') or '')
                nuevo_inicio = st.text_input('Fecha de inicio (AAAA-MM-DD)',
                                            value=str(actual.get('fecha_inicio') or ''))
                nuevo_fin = st.text_input('Fecha de finalización (AAAA-MM-DD)',
                                         value=str(actual.get('fecha_fin') or ''))
                if st.form_submit_button('Guardar proyecto', type='primary'):
                    try:
                        if nuevo_inicio: date.fromisoformat(nuevo_inicio)
                        if nuevo_fin: date.fromisoformat(nuevo_fin)
                        resultado = editar_proyecto_empresa(empresa_id,actual['id'], {
                            'nombre':nuevo_nombre.strip(),'descripcion':nueva_descripcion.strip(),
                            'fecha_inicio':nuevo_inicio.strip(),'fecha_fin':nuevo_fin.strip(),
                        })
                        if resultado:
                            st.toast('Proyecto actualizado.')
                            st.rerun()
                        else:
                            st.error('El proyecto ya no existe o no está vinculado a esta empresa.')
                    except ValueError as exc:
                        st.error(f'Revisa los campos ingresados: {exc}')
                    except Exception as exc:
                        st.error(f'No se pudo guardar el proyecto: {exc}')




def pagina_empresa(auth, seccion):
    empresa_id = auth['id']
    perfil = perfil_por_id('empresa', empresa_id)
    if not perfil:
        st.error('Este perfil empresarial ya no existe. Contacta al administrador.')
        return
    ofertas = [r['datos'] for r in ofertas_empresa(empresa_id)]
    if seccion == 'Mis proyectos':
        pagina_proyectos_empresa(empresa_id)
    elif seccion == 'Solicitudes laborales':
        pagina_solicitudes_empresa(empresa_id)
    elif seccion == 'Notificaciones':
        pagina_centro_notificaciones('empresa', empresa_id)
    elif seccion == 'Inicio':
        banner('Mi espacio · Empresa',f'Bienvenido, {perfil.get("nombre","empresa")}',
               'Publica vacantes, consulta postulaciones y descubre talento.')
        postulados = leer_datos('''
            MATCH (e:Empresa {id:$id})-[:PUBLICA]->(o:OfertaLaboral)<-[:SE_POSTULA_A|POSTULA_A]-(u:Usuario)
            RETURN count(DISTINCT u) AS total
        ''',{'id':empresa_id})
        a,b,c,d=st.columns(4)
        a.metric('Vacantes publicadas',len(ofertas))
        b.metric('Profesionales postulados',postulados[0]['total'] if postulados else 0)
        c.metric('Proyectos', len(proyectos_de_empresa(empresa_id)))
        d.metric('Solicitudes de proyecto', len(solicitudes_proyectos_empresa(empresa_id)))
        titulo_sec('Mis vacantes', 'Ofertas publicadas por tu empresa')
        if ofertas:
            for oferta in ofertas[:4]:
                job_card({**oferta, 'empresa': perfil.get('nombre')}, compact=True)
            with st.expander('Ver todas las vacantes en tabla'):
                ver_tabla(ofertas)
        else:
            st.info('Esta empresa todavía no tiene vacantes.')
        st.caption('También puedes gestionar las solicitudes laborales, candidatos y notificaciones desde el menú.')
        if st.button('Publicar una nueva vacante',type='primary'):
            st.session_state['pagina_actual']='Mis vacantes'
            st.rerun()
    elif seccion == 'Mi empresa':
        banner('Información empresarial','Mi empresa','Consulta y actualiza los datos de tu organización.')
        ficha_perfil(perfil,[('nombre','Nombre'),('industria','Industria'),
                             ('ubicacion','Ubicación'),('tamano','Tamaño'),('descripcion','Descripción')])
        titulo_sec('Empleados vinculados', 'Profesionales con relación TRABAJA_EN con esta empresa')
        ver_tabla(empleados_de_empresa(empresa_id), 'La empresa no tiene empleados vinculados todavía.')
        with st.expander('Editar información empresarial'):
            with st.form('jtg_editar_mi_empresa'):
                industria=st.text_input('Industria',value=perfil.get('industria',''))
                ubicacion=st.text_input('Ubicación',value=perfil.get('ubicacion',''))
                tamano=st.text_input('Tamaño',value=perfil.get('tamano',''))
                descripcion=st.text_area('Descripción',value=perfil.get('descripcion',''))
                if st.form_submit_button('Guardar cambios',type='primary'):
                    try:
                        r=actualizar_empresa(empresa_id,{'industria':industria.strip(),
                            'ubicacion':ubicacion.strip(),'tamano':tamano.strip(),
                            'descripcion':descripcion.strip()})
                        if r:
                            st.success('Información actualizada.')
                            st.rerun()
                        else:st.error('La empresa no existe.')
                    except Exception as exc:st.error(f'No fue posible actualizar: {exc}')
    elif seccion == 'Mis vacantes':
        banner('Empleos · Empresa','Mis vacantes','Publica y gestiona ofertas de tu organización.')
        ver_tabla(ofertas,'Todavía no has publicado ninguna vacante.')
        titulo_sec('Publicar vacante','Selecciona las habilidades que debe tener el candidato')
        habilidades_disponibles=lista('Habilidades')
        h_opts={f'{h.get("nombre","Habilidad")} · {h["id"]}':h['id'] for h in habilidades_disponibles}
        with st.form('jtg_publicar_vacante',clear_on_submit=True):
            titulo=st.text_input('Título del empleo')
            descripcion=st.text_area('Descripción y responsabilidades')
            a,b=st.columns(2)
            with a:
                ubicacion=st.text_input('Lugar de trabajo')
                salario=st.number_input('Salario en COP', min_value=0.0, value=0.0,step=100000.0,format='%.0f')
            with b:
                contrato=st.selectbox('Tipo de contrato',['Término indefinido','Término fijo','Prestación de servicios','Prácticas','Otro'])
                fecha_cierre=st.date_input('Fecha de cierre',value=date.today()+timedelta(days=30),min_value=date.today())
            habilidades=st.multiselect('Habilidades requeridas',list(h_opts))
            if st.form_submit_button('Publicar vacante',type='primary',use_container_width=True):
                if not titulo.strip() or not descripcion.strip() or not ubicacion.strip():
                    st.error('Completa el título, la descripción y la ubicación.')
                else:
                    try:
                        nuevo=publicar_vacante(empresa_id,{
                            'titulo':titulo.strip(),'descripcion':descripcion.strip(),
                            'fecha_publicacion':date.today().isoformat(),
                            'fecha_cierre':fecha_cierre.isoformat(),
                            'ubicacion':ubicacion.strip(),'salario':float(salario),
                            'tipo_contrato':contrato},[h_opts[h] for h in habilidades])
                        st.toast(f'Vacante publicada: {nuevo}')
                        st.rerun()
                    except Exception as exc:st.error(f'No se pudo publicar la vacante: {exc}')
        if ofertas:
            titulo_sec('Editar una vacante','Solo puedes editar ofertas de tu empresa')
            oferta_opts={f'{o.get("titulo","Sin título")} · {o["id"]}':o for o in ofertas}
            etiqueta=st.selectbox('Selecciona tu oferta',list(oferta_opts),key='jtg_oferta_empresa_editar')
            original=oferta_opts[etiqueta]
            with st.form(f'jtg_editar_oferta_{original["id"]}'):
                titulo=st.text_input('Título',value=original.get('titulo',''))
                descripcion=st.text_area('Descripción',value=original.get('descripcion',''))
                a,b=st.columns(2)
                with a:
                    ubicacion=st.text_input('Ubicación',value=original.get('ubicacion',''))
                    salario=st.number_input('Salario (COP)',min_value=0.0,
                         value=float(original.get('salario') or 0.0),step=100000.0)
                with b:
                    contrato=st.text_input('Contrato',value=original.get('tipo_contrato',''))
                    cierre=st.text_input('Fecha de cierre (AAAA-MM-DD)',value=str(original.get('fecha_cierre') or ''))
                if st.form_submit_button('Guardar cambios',type='primary'):
                    if not titulo.strip() or not ubicacion.strip():
                        st.error('El título y la ubicación son obligatorios.')
                    else:
                        try:
                            r=editar_vacante_propietaria(empresa_id,original['id'],{
                                'titulo':titulo.strip(),'descripcion':descripcion.strip(),
                                'fecha_cierre':cierre.strip(),'ubicacion':ubicacion.strip(),
                                'salario':float(salario),'tipo_contrato':contrato.strip()})
                            if r:
                                st.toast('Vacante actualizada.')
                                st.rerun()
                            else:st.error('Esta vacante no pertenece a tu empresa o ya no existe.')
                        except Exception as exc:st.error(f'No se pudo actualizar: {exc}')
        pagina_ciclo_vacantes(empresa_id, ofertas)
    elif seccion == 'Candidatos':
        def sugerir_candidatos(oferta_id):
            try:
                candidatos = ConsultasGrafo().candidatos_recomendados(oferta_id)
                tarjetas(candidatos,'Candidato compatible','candidato',
                         [('Distancia en red','distancia_red')],
                         score_key='competencias_coincidentes',lista_key='habilidades_coincidentes')
            except Exception as exc:
                st.warning('Las recomendaciones no están disponibles en este momento.')
                with st.expander('Detalles técnicos'):
                    st.exception(exc)
        pagina_candidatos_empresa(empresa_id, ofertas, sugerir_candidatos)



# Verificar la conexión antes de buscar perfiles existentes.
if not all([os.getenv('NEO4J_URI'),os.getenv('NEO4J_USERNAME'),os.getenv('NEO4J_PASSWORD')]):
    st.error('Faltan las variables NEO4J_URI, NEO4J_USERNAME o NEO4J_PASSWORD en .env.')
    st.stop()
try:
    db.connect()
except Exception as exc:
    st.error('No fue posible conectar con la base de datos Neo4j.')
    with st.expander('Detalles técnicos'):
        st.exception(exc)
    st.stop()

if not st.session_state.get('jtg_auth'):
    pantalla_login()
    st.stop()

# Mantener accesible el control para reabrir la barra lateral.
# En la pantalla de inicio de sesion permanece oculta.
st.markdown('''<style>
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: .65rem !important;
    left: .65rem !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
}
[data-testid="stSidebarCollapsedControl"] button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: #1d4ed8 !important;
    background: #ffffff !important;
    border: 1px solid #bfd4f5 !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(34,83,150,.12) !important;
    pointer-events: auto !important;
}
[data-testid="stSidebarCollapseButton"] {visibility: visible !important;}
</style>''', unsafe_allow_html=True)

auth = st.session_state['jtg_auth']
if auth.get('rol') == 'admin':
    NAVEGACION = [
        ('Inicio','Principal'),('Usuarios','Gestión'),('Empresas','Gestión'),
        ('Habilidades','Gestión'),('Tecnologías','Gestión'),('Proyectos','Gestión'),
        ('Empleos','Gestión'),('Conexiones','Red y análisis'),
        ('Explorador del grafo','Red y análisis'),('Recomendaciones','Red y análisis'),
        ('Consultas','Red y análisis'),('Configuración','Sistema'),
    ]
elif auth.get('rol') == 'profesional':
    NAVEGACION = [('Inicio','Mi espacio'),('Mi perfil','Mi espacio'),
                  ('Mi empresa laboral','Mi espacio'),('Buscar empleos','Oportunidades'),
                  ('Empleos guardados','Oportunidades'),('Mis postulaciones','Oportunidades'),
                  ('Recomendaciones','Oportunidades'),('Mi red','Mi red'),
                  ('Proyectos de mi empresa','Mi red'),('Notificaciones','Mi red')]
elif auth.get('rol') == 'empresa':
    NAVEGACION = [('Inicio','Mi empresa'),('Mi empresa','Mi empresa'),
                  ('Mis proyectos','Mi empresa'),('Solicitudes laborales','Mi empresa'),
                  ('Mis vacantes','Empleo'),('Candidatos','Empleo'),
                  ('Notificaciones','Empleo')]
else:
    st.session_state.pop('jtg_auth', None)
    st.rerun()

st.sidebar.markdown('''<div class="jt-logo-line"><div class="jt-logo-mark">J</div>
    <div class="jt-logo-wordmark">Job to go</div></div>
    <div class="jt-logo-subtitle">Conectamos talento con oportunidades</div>''', unsafe_allow_html=True)
st.sidebar.markdown(
    '<div class="jt-side-account"><div class="jt-account-avatar">'+ui_safe(ui_initials(auth.get('nombre')))+
    '</div><div><div class="jt-account-title">'+ui_safe(auth.get('nombre'))+'</div><div class="jt-account-role">'+
    ui_safe({'admin':'Administrador','profesional':'Profesional','empresa':'Empresa'}.get(auth['rol'],''))+
    '</div></div></div>', unsafe_allow_html=True)


if st.session_state.get('pagina_actual') not in {nombre for nombre, _ in NAVEGACION}:
    st.session_state['pagina_actual'] = 'Inicio'

def navegar_a(pagina):
    st.session_state['pagina_actual'] = pagina

ultimo_grupo = None
for nombre, grupo in NAVEGACION:
    if grupo != ultimo_grupo:
        st.sidebar.markdown(f'<div class="jtg-sidebar-caption">{limpio(grupo)}</div>',unsafe_allow_html=True)
        ultimo_grupo = grupo
    etiqueta_boton = nombre
    if nombre == 'Mi red' and auth['rol'] == 'profesional':
        try:
            nuevas = len(solicitudes_recibidas(auth['id']))
            if nuevas:
                etiqueta_boton = f'Mi red · {nuevas} pendiente(s)'
        except Exception:
            pass  # La página seguirá mostrando el error real si falla Neo4j.
    if nombre == 'Notificaciones' and auth['rol'] in ('profesional', 'empresa'):
        try:
            n = sum(1 for e in notificaciones(auth['rol'], auth['id']) if not e['leida'])
            if n: etiqueta_boton = f'Notificaciones · {n} nuevas'
        except Exception:
            pass
    st.sidebar.button(etiqueta_boton,key=f'menu_{nombre.lower().replace(" ", "_")}',use_container_width=True,
                      type='primary' if st.session_state['pagina_actual'] == nombre else 'secondary',
                      on_click=navegar_a,args=(nombre,))
st.sidebar.divider()
if st.sidebar.button('Cerrar sesión',use_container_width=True):
    st.session_state.pop('jtg_auth',None)
    st.session_state['pagina_actual']='Inicio'
    st.rerun()
st.sidebar.caption('Datos conectados a Neo4j')

seccion = st.session_state['pagina_actual']
st.markdown(
    '<div class="jt-topbar"><div class="jt-topbar-left">Job to go <span>/</span><strong>' +
    ui_safe(seccion) + '</strong></div><div class="jt-topbar-right">'
    '<span class="jt-online"></span> Conexión activa</div></div>',
    unsafe_allow_html=True)

try:
    if auth['rol'] == 'profesional':
        pagina_profesional(auth,seccion)
    elif auth['rol'] == 'empresa':
        pagina_empresa(auth,seccion)
    else:
        if seccion == 'Inicio': pagina_inicio()
        elif seccion == 'Usuarios': pagina_crud('Usuarios')
        elif seccion == 'Empresas': pagina_crud('Empresas')
        elif seccion == 'Habilidades': pagina_crud('Habilidades')
        elif seccion == 'Tecnologías': pagina_crud('Tecnologías')
        elif seccion == 'Proyectos': pagina_crud('Proyectos')
        elif seccion == 'Empleos': pagina_empleos()
        elif seccion == 'Conexiones': pagina_conexiones()
        elif seccion == 'Explorador del grafo': pagina_grafo()
        elif seccion == 'Recomendaciones': pagina_recomendaciones()
        elif seccion == 'Consultas': pagina_consultas()
        else:
            banner('Herramientas','Configuración','Mantenimiento del proyecto académico.')
            st.write('**Base de datos:**',os.getenv('NEO4J_URI','Sin configurar'))
            st.write('**Usuario de Neo4j:**',os.getenv('NEO4J_USERNAME','Sin configurar'))
            if st.button('Crear restricciones de unicidad'):
                ejecutar(crear_restricciones_unicidad)
except Exception as exc:
    st.error('No fue posible completar la consulta. No se sustituyeron datos por información simulada.')
    with st.expander('Ver error técnico'):
        st.exception(exc)
