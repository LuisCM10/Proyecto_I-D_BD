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
