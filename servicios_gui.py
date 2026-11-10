"""Consultas de lectura para la interfaz.

No reemplaza los repositorios existentes; ofrece consultas para presentar sus datos.
Los nombres de etiquetas se validan contra un catálogo local (nunca llegan del usuario).
"""
from conexion import db

ETIQUETAS = {
    "Usuarios": ("Usuario", "nombre"),
    "Empresas": ("Empresa", "nombre"),
    "Habilidades": ("Habilidad", "nombre"),
    "Proyectos": ("Proyecto", "nombre"),
    "Ofertas laborales": ("OfertaLaboral", "titulo"),
    "Tecnologías": ("Tecnologia", "nombre"),
}


def listar_entidades(seccion: str):
    etiqueta, campo = ETIQUETAS[seccion]
    return db.ejecutar_consulta(
        f"MATCH (n:{etiqueta}) RETURN properties(n) AS datos ORDER BY n.{campo}",
        write=False,
    )


def total_entidades():
    return db.ejecutar_consulta("""
    MATCH (n)
    WHERE n:Usuario OR n:Empresa OR n:Habilidad OR n:Proyecto OR n:OfertaLaboral
    WITH labels(n)[0] AS tipo, count(n) AS total
    RETURN tipo, total
    """, write=False)


def total_relaciones():
    res = db.ejecutar_consulta("MATCH ()-[r]->() RETURN count(r) AS total", write=False)
    return res[0]["total"] if res else 0


def ultimas_ofertas(limite=8):
    return db.ejecutar_consulta("""
    MATCH (o:OfertaLaboral)
    OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o)
    RETURN o.id AS id, o.titulo AS titulo, o.ubicacion AS ubicacion,
           o.salario AS salario, o.tipo_contrato AS contrato,
           o.fecha_cierre AS fecha_cierre, e.nombre AS empresa
    ORDER BY o.fecha_publicacion DESC, o.titulo
    LIMIT $limite
    """, {"limite": limite}, write=False)


def datos_grafo(tipos=None, limite=120):
    """Nodos seleccionados y sus relaciones internas, inclusive nodos aislados."""
    permitidos = [ETIQUETAS[x][0] for x in (tipos or ETIQUETAS.keys())]
    if not permitidos:
        return []
    return db.ejecutar_consulta("""
    MATCH (n)
    WHERE any(l IN labels(n) WHERE l IN $tipos)
    WITH n ORDER BY coalesce(n.nombre, n.titulo, n.id)
    LIMIT $limite
    WITH collect(n) AS nodos
    UNWIND nodos AS n
    OPTIONAL MATCH (n)-[r]->(m)
    WHERE m IN nodos
    RETURN n.id AS origen_id, head(labels(n)) AS origen_tipo,
           coalesce(n.nombre, n.titulo, n.id) AS origen_nombre,
           m.id AS destino_id, head(labels(m)) AS destino_tipo,
           coalesce(m.nombre, m.titulo, m.id) AS destino_nombre,
           type(r) AS relacion
    """, {"tipos": permitidos, "limite": int(limite)}, write=False)


def habilidades_de_usuario(usuario_id):
    return db.ejecutar_consulta("""
    MATCH (u:Usuario {id: $id})-[:POSEE]->(h:Habilidad)
    RETURN h.nombre AS habilidad ORDER BY h.nombre
    """, {"id": usuario_id}, write=False)


def postulaciones_de_usuario(usuario_id):
    return db.ejecutar_consulta("""
    MATCH (u:Usuario {id: $id})-[:SE_POSTULA_A]->(o:OfertaLaboral)
    RETURN o.titulo AS oferta, o.id AS id ORDER BY o.titulo
    """, {"id": usuario_id}, write=False)
