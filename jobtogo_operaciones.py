"""Operaciones del portal de profesional / empresa en Neo4j.

Siempre usa el ID del perfil autenticado, y los Cypher de empresa
restringen escrituras mediante la relación PUBLICA de esa empresa.
"""
from __future__ import annotations

from conexion import db
from entidades.controller import obtener_siguiente_id
from entidades.usuario import Usuario
from entidades.empresa import Empresa


def consulta(cypher, params=None):
    return db.ejecutar_consulta(cypher, params or {}, write=False)


def comprobar_correo_nuevo(correo):
    filas = consulta('''MATCH (u:Usuario)
        WHERE toLower(trim(u.correo)) = toLower(trim($correo))
        RETURN count(u) AS total''', {'correo': correo})
    return int(filas[0]['total']) == 0 if filas else True


def comprobar_empresa_nueva(nombre):
    filas = consulta('''MATCH (e:Empresa)
        WHERE toLower(trim(e.nombre)) = toLower(trim($nombre))
        RETURN count(e) AS total''', {'nombre': nombre})
    return int(filas[0]['total']) == 0 if filas else True


def crear_perfil(rol, datos):
    """Crea SOLO un nodo del modelo existente. Devuelve su ID."""
    if rol == 'profesional':
        if not comprobar_correo_nuevo(datos['correo']):
            raise ValueError('Ese correo ya pertenece a un profesional. Pide al administrador que vincule tu cuenta.')
        resultado = Usuario().crear(**datos)
        etiqueta = 'u'
    elif rol == 'empresa':
        if not comprobar_empresa_nueva(datos['nombre']):
            raise ValueError('La empresa ya existe. Pide al administrador que vincule su acceso.')
        resultado = Empresa().crear(**datos)
        etiqueta = 'e'
    else:
        raise ValueError('Tipo de cuenta no permitido.')
    if not resultado or not resultado[0].get(etiqueta):
        raise RuntimeError('No se pudo crear el perfil en Neo4j.')
    return resultado[0][etiqueta]['id']


def revertir_perfil_nuevo(rol, id_nuevo):
    """Solo utilizar ante un error en el alta inmediatamente después de CREATE."""
    if rol == 'profesional':
        Usuario().eliminar(id_nuevo)
    elif rol == 'empresa':
        Empresa().eliminar(id_nuevo)


def actualizar_profesional(usuario_id, datos):
    # El correo no se modifica aquí: está asociado a la credencial local.
    return db.ejecutar_consulta('''
      MATCH (u:Usuario {id:$id})
      SET u.nombre=$nombre, u.telefono=$telefono, u.ubicacion=$ubicacion,
          u.experiencia=$experiencia, u.educacion=$educacion
      RETURN u.id AS id
    ''', {'id':usuario_id, **datos})


def actualizar_empresa(empresa_id, datos):
    return db.ejecutar_consulta('''
      MATCH (e:Empresa {id:$id})
      SET e.industria=$industria, e.ubicacion=$ubicacion,
          e.tamano=$tamano, e.descripcion=$descripcion
      RETURN e.id AS id
    ''', {'id':empresa_id, **datos})


def consultar_postulaciones(usuario_id):
    return consulta('''
      MATCH (u:Usuario {id:$id})-[:SE_POSTULA_A|POSTULA_A]->(o:OfertaLaboral)
      OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o)
      RETURN DISTINCT o.id AS id, o.titulo AS oferta, e.nombre AS empresa,
             o.ubicacion AS ubicacion, o.fecha_cierre AS fecha_cierre
      ORDER BY oferta
    ''', {'id': usuario_id})


def postularse(usuario_id, oferta_id):
    return db.ejecutar_consulta('''
      MATCH (u:Usuario {id:$usuario_id}), (o:OfertaLaboral {id:$oferta_id})
      MERGE (u)-[r:SE_POSTULA_A]->(o)
      RETURN u.id AS usuario_id, o.id AS oferta_id
    ''', {'usuario_id':usuario_id,'oferta_id':oferta_id})


def publicar_vacante(empresa_id, datos, habilidad_ids):
    """Crea oferta + relación PUBLICA + requisitos en una sola consulta de escritura.

    El incremento previo de Contador sigue el patrón del proyecto original.
    """
    if not empresa_id:
        raise ValueError('No se encontró la empresa propietaria.')
    if not consulta('MATCH (e:Empresa {id:$id}) RETURN e.id AS id', {'id':empresa_id}):
        raise ValueError('La empresa no existe en Neo4j.')
    ids = list(dict.fromkeys(habilidad_ids))
    if ids:
        existentes = consulta('MATCH (h:Habilidad) WHERE h.id IN $ids RETURN h.id AS id', {'ids':ids})
        if len(existentes) != len(ids):
            raise ValueError('Hay habilidades seleccionadas que ya no existen.')
    oferta_id = obtener_siguiente_id('OfertaLaboral', 'ofe')
    params = {'empresa_id': empresa_id, 'id': oferta_id, 'habilidades': ids, **datos}
    resultado = db.ejecutar_consulta('''
      MATCH (e:Empresa {id:$empresa_id})
      CREATE (o:OfertaLaboral {
          id:$id, titulo:$titulo, descripcion:$descripcion,
          fecha_publicacion:$fecha_publicacion, fecha_cierre:$fecha_cierre,
          ubicacion:$ubicacion, salario:$salario, tipo_contrato:$tipo_contrato
      })
      MERGE (e)-[:PUBLICA]->(o)
      WITH o
      OPTIONAL MATCH (h:Habilidad) WHERE h.id IN $habilidades
      FOREACH (_ IN CASE WHEN h IS NOT NULL THEN [1] ELSE [] END |
          MERGE (o)-[:REQUIERE_TENER]->(h))
      RETURN DISTINCT o.id AS id
    ''', params)
    if not resultado:
        raise RuntimeError('No se pudo publicar la oferta para esta empresa.')
    return resultado[0]['id']


def editar_vacante_propietaria(empresa_id, oferta_id, datos):
    """Impide cambiar vacantes de otras empresas incluso con un ID manipulado."""
    return db.ejecutar_consulta('''
      MATCH (e:Empresa {id:$empresa_id})-[:PUBLICA]->(o:OfertaLaboral {id:$oferta_id})
      SET o.titulo=$titulo, o.descripcion=$descripcion, o.fecha_cierre=$fecha_cierre,
          o.ubicacion=$ubicacion, o.salario=$salario, o.tipo_contrato=$tipo_contrato
      RETURN o.id AS id
    ''', {'empresa_id':empresa_id,'oferta_id':oferta_id, **datos})

# ---------------------------------------------------------------------------
# Funciones nuevas: habilidades del profesional y proyectos de la empresa.
# No se crean nuevas etiquetas en Neo4j, solo relaciones/nodos del modelo.
# ---------------------------------------------------------------------------

def habilidades_catalogo():
    """Lista habilidades existentes, sin duplicarlas ni cambiar su esquema."""
    return consulta('''
        MATCH (h:Habilidad)
        RETURN h.id AS id, h.nombre AS nombre
        ORDER BY toLower(h.nombre), h.id
    ''')


def ids_habilidades_usuario(usuario_id):
    return [fila['id'] for fila in consulta('''
        MATCH (u:Usuario {id:$id})-[:POSEE]->(h:Habilidad)
        RETURN DISTINCT h.id AS id
    ''', {'id': usuario_id})]


def actualizar_habilidades_profesional(usuario_id, habilidad_ids):
    """Sincroniza solo relaciones POSEE de este usuario. No toca otras personas."""
    ids = list(dict.fromkeys(habilidad_ids or []))
    if ids:
        disponibles = consulta('''
            MATCH (h:Habilidad) WHERE h.id IN $ids RETURN h.id AS id
        ''', {'ids': ids})
        if {r['id'] for r in disponibles} != set(ids):
            raise ValueError('Una de las habilidades seleccionadas ya no existe.')
    resultado = db.ejecutar_consulta('''
        MATCH (u:Usuario {id:$usuario_id})
        OPTIONAL MATCH (u)-[r:POSEE]->(:Habilidad)
        WITH u, collect(r) AS anteriores
        FOREACH (rel IN anteriores | DELETE rel)
        WITH u
        OPTIONAL MATCH (h:Habilidad) WHERE h.id IN $habilidades
        WITH u, collect(DISTINCT h) AS nuevas
        FOREACH (h IN nuevas | MERGE (u)-[:POSEE]->(h))
        RETURN u.id AS id, size(nuevas) AS total_habilidades
    ''', {'usuario_id': usuario_id, 'habilidades': ids})
    if not resultado:
        raise ValueError('No se encontró el perfil profesional.')
    return resultado[0]


def proyectos_de_empresa(empresa_id):
    """Solo proyectos asociados a la empresa mediante TIENE."""
    return consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto)
        OPTIONAL MATCH (p)-[:USA_TECNOLOGIA]->(t:Tecnologia)
        RETURN p.id AS id, p.nombre AS nombre, p.descripcion AS descripcion,
               p.fecha_inicio AS fecha_inicio, p.fecha_fin AS fecha_fin,
               collect(DISTINCT t.nombre) AS tecnologias
        ORDER BY nombre
    ''', {'empresa_id': empresa_id})


def tecnologias_catalogo():
    return consulta('''
        MATCH (t:Tecnologia)
        RETURN t.id AS id, t.nombre AS nombre
        ORDER BY toLower(t.nombre), t.id
    ''')


def crear_proyecto_empresa(empresa_id, datos, tecnologia_ids=None):
    """Crea un Proyecto de esa Empresa, vinculado con TIENE y USA_TECNOLOGIA.

    Crea proyecto y relaciones en una sola escritura. El contador de IDs se
    actualiza antes, igual que en las entidades originales del repositorio.
    """
    if not empresa_id:
        raise ValueError('No hay empresa activa.')
    if not (datos.get('nombre') or '').strip():
        raise ValueError('Indica el nombre del proyecto.')
    if not consulta('MATCH (e:Empresa {id:$id}) RETURN e.id AS id', {'id':empresa_id}):
        raise ValueError('No existe la empresa seleccionada.')
    ids = list(dict.fromkeys(tecnologia_ids or []))
    if ids:
        disponibles = consulta('''
            MATCH (t:Tecnologia) WHERE t.id IN $ids RETURN t.id AS id
        ''', {'ids': ids})
        if {r['id'] for r in disponibles} != set(ids):
            raise ValueError('Una tecnología seleccionada ya no existe.')
    if datos.get('fecha_fin') and datos.get('fecha_inicio') and datos['fecha_fin'] < datos['fecha_inicio']:
        raise ValueError('La fecha final no puede ser anterior a la inicial.')

    proyecto_id = obtener_siguiente_id(entidad='Proyecto', prefijo='proy')
    parametros = {
        'empresa_id': empresa_id, 'id': proyecto_id,
        'nombre': datos['nombre'].strip(),
        'descripcion': (datos.get('descripcion') or '').strip(),
        'fecha_inicio': datos.get('fecha_inicio') or '',
        'fecha_fin': datos.get('fecha_fin') or '',
        'tecnologias': ids,
    }
    resultado = db.ejecutar_consulta('''
        MATCH (e:Empresa {id:$empresa_id})
        CREATE (p:Proyecto {
            id:$id, nombre:$nombre, descripcion:$descripcion,
            fecha_inicio:$fecha_inicio, fecha_fin:$fecha_fin
        })
        MERGE (e)-[:TIENE]->(p)
        WITH p
        OPTIONAL MATCH (t:Tecnologia) WHERE t.id IN $tecnologias
        WITH p, collect(DISTINCT t) AS tecnologias
        FOREACH (t IN tecnologias | MERGE (p)-[:USA_TECNOLOGIA]->(t))
        RETURN p.id AS id
    ''', parametros)
    if not resultado:
        raise RuntimeError('No se pudo crear el proyecto empresarial.')
    return resultado[0]['id']


def editar_proyecto_empresa(empresa_id, proyecto_id, datos):
    """Permite editar solo proyectos vinculados a la empresa iniciada."""
    if not (datos.get('nombre') or '').strip():
        raise ValueError('Indica el nombre del proyecto.')
    if datos.get('fecha_fin') and datos.get('fecha_inicio') and datos['fecha_fin'] < datos['fecha_inicio']:
        raise ValueError('La fecha final no puede ser anterior a la inicial.')
    return db.ejecutar_consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto {id:$proyecto_id})
        SET p.nombre=$nombre, p.descripcion=$descripcion,
            p.fecha_inicio=$fecha_inicio, p.fecha_fin=$fecha_fin
        RETURN p.id AS id
    ''', {'empresa_id': empresa_id, 'proyecto_id': proyecto_id,
          'nombre': datos['nombre'].strip(),
          'descripcion': (datos.get('descripcion') or '').strip(),
          'fecha_inicio': datos.get('fecha_inicio') or '',
          'fecha_fin': datos.get('fecha_fin') or ''})