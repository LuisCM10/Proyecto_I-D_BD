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
          ubicacion:$ubicacion, salario:$salario, tipo_contrato:$tipo_contrato,
          estado:'Abierta'
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

# ---------------------------------------------------------------------------
# Solicitudes de conexión profesional (sin crear etiquetas / nodos nuevos).
# Las solicitudes pendientes son SOLICITA_CONEXION; solo al aceptar se crea
# CONECTA_CON. Las consultas y recomendaciones existentes no toman pendientes
# como conexiones consolidadas.
# ---------------------------------------------------------------------------

def profesionales_para_conectar(usuario_id, limite=120):
    """Solo otros profesionales sin conexión y sin solicitud en ningún sentido."""
    return consulta('''
        MATCH (yo:Usuario {id:$id})
        MATCH (otro:Usuario)
        WHERE otro.id <> yo.id AND otro.id IS NOT NULL
          AND NOT EXISTS { MATCH (yo)-[:CONECTA_CON]-(otro) }
          AND NOT EXISTS { MATCH (yo)-[:SOLICITA_CONEXION]-(otro) }
        RETURN otro.id AS id, otro.nombre AS nombre, otro.ubicacion AS ubicacion,
               otro.experiencia AS experiencia
        ORDER BY toLower(otro.nombre), otro.id
        LIMIT $limite
    ''', {'id': usuario_id, 'limite': limite})


def solicitudes_recibidas(usuario_id):
    return consulta('''
        MATCH (solicitante:Usuario)-[s:SOLICITA_CONEXION]->(yo:Usuario {id:$id})
        RETURN solicitante.id AS id, solicitante.nombre AS nombre,
               solicitante.ubicacion AS ubicacion,
               solicitante.experiencia AS experiencia,
               s.enviada_en AS fecha
        ORDER BY nombre, id
    ''', {'id': usuario_id})


def solicitudes_enviadas(usuario_id):
    return consulta('''
        MATCH (yo:Usuario {id:$id})-[s:SOLICITA_CONEXION]->(destino:Usuario)
        RETURN destino.id AS id, destino.nombre AS nombre,
               destino.ubicacion AS ubicacion, s.enviada_en AS fecha
        ORDER BY nombre, id
    ''', {'id': usuario_id})


def contactos_de_profesional(usuario_id):
    return consulta('''
        MATCH (yo:Usuario {id:$id})-[:CONECTA_CON]-(contacto:Usuario)
        RETURN DISTINCT contacto.id AS id, contacto.nombre AS nombre,
               contacto.ubicacion AS ubicacion, contacto.experiencia AS experiencia
        ORDER BY nombre, id
    ''', {'id': usuario_id})


def solicitar_conexion(usuario_id, destinatario_id):
    """No envía una solicitud al propio perfil, un contacto o un pendiente."""
    if not usuario_id or not destinatario_id or usuario_id == destinatario_id:
        raise ValueError('Selecciona a otro profesional para enviar una solicitud.')
    r = db.ejecutar_consulta('''
        MATCH (yo:Usuario {id:$origen}), (otro:Usuario {id:$destino})
        WHERE yo <> otro
          AND NOT EXISTS { MATCH (yo)-[:CONECTA_CON]-(otro) }
          AND NOT EXISTS { MATCH (yo)-[:SOLICITA_CONEXION]-(otro) }
        MERGE (yo)-[s:SOLICITA_CONEXION]->(otro)
        ON CREATE SET s.enviada_en = toString(datetime())
        RETURN yo.id AS origen, otro.id AS destino
    ''', {'origen': usuario_id, 'destino': destinatario_id})
    if not r:
        raise ValueError('Ya existe una conexión o una solicitud entre estos profesionales.')
    return r[0]


def aceptar_solicitud(usuario_id, solicitante_id):
    """Únicamente el destinatario de la solicitud puede aceptarla."""
    r = db.ejecutar_consulta('''
        MATCH (origen:Usuario {id:$origen})-[sol:SOLICITA_CONEXION]->(yo:Usuario {id:$destino})
        MERGE (origen)-[conexion:CONECTA_CON]->(yo)
        ON CREATE SET conexion.aceptada_en = toString(datetime())
        DELETE sol
        RETURN origen.id AS origen, yo.id AS destino
    ''', {'origen': solicitante_id, 'destino': usuario_id})
    if not r:
        raise ValueError('La solicitud ya no está pendiente o no te corresponde.')
    return r[0]


def rechazar_solicitud(usuario_id, solicitante_id):
    """Elimina únicamente la invitación dirigida al perfil en sesión."""
    r = db.ejecutar_consulta('''
        MATCH (origen:Usuario {id:$origen})-[sol:SOLICITA_CONEXION]->(yo:Usuario {id:$destino})
        WITH origen.id AS origen_id, yo.id AS destino_id, sol
        DELETE sol
        RETURN origen_id AS origen, destino_id AS destino
    ''', {'origen': solicitante_id, 'destino': usuario_id})
    if not r:
        raise ValueError('La solicitud ya no está pendiente o no te corresponde.')
    return r[0]


def cancelar_solicitud(usuario_id, destinatario_id):
    """Solo el remitente puede cancelar su propia invitación."""
    r = db.ejecutar_consulta('''
        MATCH (yo:Usuario {id:$origen})-[sol:SOLICITA_CONEXION]->(otro:Usuario {id:$destino})
        WITH yo.id AS origen_id, otro.id AS destino_id, sol
        DELETE sol
        RETURN origen_id AS origen, destino_id AS destino
    ''', {'origen': usuario_id, 'destino': destinatario_id})
    if not r:
        raise ValueError('No se encontró esa solicitud enviada.')
    return r[0]

# ---------------------------------------------------------------------------
# Vinculación laboral visible y solicitudes para participar en proyectos.
# Usa las relaciones existentes TRABAJA_EN, TIENE y PARTICIPA_EN.
# Solo se agrega SOLICITA_PARTICIPACION para las solicitudes pendientes.
# No crea etiquetas ni modifica los nodos existentes.
# ---------------------------------------------------------------------------

def empresas_de_profesional(usuario_id):
    """Empresas donde el profesional tiene una relación TRABAJA_EN."""
    return consulta('''
        MATCH (u:Usuario {id:$usuario_id})-[:TRABAJA_EN]->(e:Empresa)
        OPTIONAL MATCH (e)-[:TIENE]->(p:Proyecto)
        RETURN e.id AS id, e.nombre AS nombre, e.industria AS industria,
               e.ubicacion AS ubicacion, count(DISTINCT p) AS total_proyectos
        ORDER BY nombre, id
    ''', {'usuario_id': usuario_id})


def empleados_de_empresa(empresa_id):
    """Solo profesionales con relación laboral vigente hacia esta empresa."""
    return consulta('''
        MATCH (u:Usuario)-[:TRABAJA_EN]->(e:Empresa {id:$empresa_id})
        RETURN DISTINCT u.id AS id, u.nombre AS nombre,
               u.correo AS correo, u.ubicacion AS ubicacion
        ORDER BY nombre, id
    ''', {'empresa_id': empresa_id})


def proyectos_para_profesional(usuario_id):
    """Proyectos de sus empresas con el estado de participación individual."""
    return consulta('''
        MATCH (u:Usuario {id:$usuario_id})-[:TRABAJA_EN]->(e:Empresa)-[:TIENE]->(p:Proyecto)
        OPTIONAL MATCH (p)-[:USA_TECNOLOGIA]->(t:Tecnologia)
        WITH u, e, p, collect(DISTINCT t.nombre) AS tecnologias
        RETURN p.id AS id, p.nombre AS nombre, p.descripcion AS descripcion,
               p.fecha_inicio AS fecha_inicio, p.fecha_fin AS fecha_fin,
               e.id AS empresa_id, e.nombre AS empresa,
               tecnologias,
               CASE WHEN EXISTS { MATCH (u)-[:PARTICIPA_EN]->(p) } THEN 'Participando'
                    WHEN EXISTS { MATCH (u)-[:SOLICITA_PARTICIPACION]->(p) } THEN 'Pendiente'
                    ELSE 'Disponible' END AS estado
        ORDER BY empresa, nombre, id
    ''', {'usuario_id': usuario_id})


def participaciones_de_profesional(usuario_id):
    """Proyectos en los que realmente participa, aun si cambió de empresa."""
    return consulta('''
        MATCH (u:Usuario {id:$usuario_id})-[:PARTICIPA_EN]->(p:Proyecto)
        OPTIONAL MATCH (e:Empresa)-[:TIENE]->(p)
        RETURN DISTINCT p.id AS id, p.nombre AS nombre,
               p.descripcion AS descripcion, e.nombre AS empresa
        ORDER BY nombre, id
    ''', {'usuario_id': usuario_id})


def solicitar_participacion_proyecto(usuario_id, proyecto_id):
    """Solicita participar solo si TRABAJA_EN la empresa dueña del proyecto."""
    if not usuario_id or not proyecto_id:
        raise ValueError('Falta identificar al profesional o al proyecto.')
    resultado = db.ejecutar_consulta('''
        MATCH (u:Usuario {id:$usuario_id})-[:TRABAJA_EN]->(e:Empresa)-[:TIENE]->(p:Proyecto {id:$proyecto_id})
        WHERE NOT EXISTS { MATCH (u)-[:PARTICIPA_EN]->(p) }
          AND NOT EXISTS { MATCH (u)-[:SOLICITA_PARTICIPACION]->(p) }
        MERGE (u)-[s:SOLICITA_PARTICIPACION]->(p)
        ON CREATE SET s.enviada_en = toString(datetime())
        RETURN u.id AS usuario_id, p.id AS proyecto_id, e.id AS empresa_id
    ''', {'usuario_id': usuario_id, 'proyecto_id': proyecto_id})
    if not resultado:
        raise ValueError('No puedes solicitar este proyecto: ya participas, tienes una solicitud pendiente o no trabajas en la empresa.')
    return resultado[0]


def cancelar_participacion_proyecto(usuario_id, proyecto_id):
    """El profesional puede cancelar únicamente su propia solicitud pendiente."""
    resultado = db.ejecutar_consulta('''
        MATCH (u:Usuario {id:$usuario_id})-[s:SOLICITA_PARTICIPACION]->(p:Proyecto {id:$proyecto_id})
        WITH u.id AS usuario_id, p.id AS proyecto_id, s
        DELETE s
        RETURN usuario_id, proyecto_id
    ''', {'usuario_id': usuario_id, 'proyecto_id': proyecto_id})
    if not resultado:
        raise ValueError('Esta solicitud ya no está pendiente.')
    return resultado[0]


def solicitudes_proyectos_empresa(empresa_id):
    """Solicitudes recibidas para proyectos propiedad de la empresa."""
    return consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto)
              <-[s:SOLICITA_PARTICIPACION]-(u:Usuario)
        RETURN DISTINCT p.id AS proyecto_id, p.nombre AS proyecto,
               u.id AS usuario_id, u.nombre AS profesional,
               u.correo AS correo, s.enviada_en AS fecha,
               EXISTS { MATCH (u)-[:TRABAJA_EN]->(e) } AS es_empleado
        ORDER BY proyecto, profesional
    ''', {'empresa_id': empresa_id})


def participantes_proyectos_empresa(empresa_id):
    """Personas cuya participación ya fue aceptada o registrada previamente."""
    return consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto)<-[:PARTICIPA_EN]-(u:Usuario)
        RETURN DISTINCT p.id AS proyecto_id, p.nombre AS proyecto,
               u.id AS usuario_id, u.nombre AS profesional,
               u.correo AS correo
        ORDER BY proyecto, profesional
    ''', {'empresa_id': empresa_id})


def aceptar_participacion_proyecto(empresa_id, usuario_id, proyecto_id):
    """Únicamente la empresa propietaria aprueba solicitudes de sus empleados."""
    resultado = db.ejecutar_consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto {id:$proyecto_id})
              <-[sol:SOLICITA_PARTICIPACION]-(u:Usuario {id:$usuario_id})
        MATCH (u)-[:TRABAJA_EN]->(e)
        MERGE (u)-[participacion:PARTICIPA_EN]->(p)
        ON CREATE SET participacion.aprobada_en = toString(datetime())
        DELETE sol
        RETURN e.id AS empresa_id, p.id AS proyecto_id, u.id AS usuario_id
    ''', {'empresa_id': empresa_id, 'usuario_id': usuario_id, 'proyecto_id': proyecto_id})
    if not resultado:
        raise ValueError('La solicitud no existe, el proyecto no es tuyo o el profesional ya no trabaja en la empresa.')
    return resultado[0]


def rechazar_participacion_proyecto(empresa_id, usuario_id, proyecto_id):
    """Solo el dueño del proyecto puede rechazar la solicitud pendiente."""
    resultado = db.ejecutar_consulta('''
        MATCH (e:Empresa {id:$empresa_id})-[:TIENE]->(p:Proyecto {id:$proyecto_id})
              <-[sol:SOLICITA_PARTICIPACION]-(u:Usuario {id:$usuario_id})
        WITH e.id AS empresa_id, p.id AS proyecto_id, u.id AS usuario_id, sol
        DELETE sol
        RETURN empresa_id, proyecto_id, usuario_id
    ''', {'empresa_id': empresa_id, 'usuario_id': usuario_id, 'proyecto_id': proyecto_id})
    if not resultado:
        raise ValueError('La solicitud ya no existe o el proyecto no pertenece a tu empresa.')
    return resultado[0]
