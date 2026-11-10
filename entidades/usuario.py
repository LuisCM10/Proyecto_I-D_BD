from typing import Any, Dict, List, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id


class Usuario:

    def crear(self, nombre: str, correo: str, telefono: str = "", ubicacion: str = "", experiencia: str = "", educacion: str = "") -> List[Dict[str, Any]]:
        usuario_id = obtener_siguiente_id(entidad="Usuario", prefijo="usr")
        """Crea un nodo Usuario con sus propiedades: (nombre, correo, teléfono, ubicación, experiencia, educación)."""
        query = """
        CREATE (u:Usuario {
            id: $id,
            nombre: $nombre,
            correo: $correo,
            telefono: $telefono,
            ubicacion: $ubicacion,
            experiencia: $experiencia,
            educacion: $educacion
        })
        RETURN u
        """
        params = {
            "id": usuario_id,
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "ubicacion": ubicacion,
            "experiencia": experiencia,
            "educacion": educacion,
        }
        return db.ejecutar_consulta(query, params)
    
    def actualizar(self, usuario_id: str, nombre: Optional[str] = None, correo: Optional[str] = None, telefono: Optional[str] = None, ubicacion: Optional[str] = None, experiencia: Optional[str] = None, educacion: Optional[str] = None) -> List[Dict[str, Any]]:
        """Actualiza la información personal y profesional de un usuario."""
        query = """
        MATCH (u:Usuario {id: $id})
        SET u.nombre = COALESCE($nombre, u.nombre),
            u.correo = COALESCE($correo, u.correo),
            u.telefono = COALESCE($telefono, u.telefono),
            u.ubicacion = COALESCE($ubicacion, u.ubicacion),
            u.experiencia = COALESCE($experiencia, u.experiencia),
            u.educacion = COALESCE($educacion, u.educacion)
        RETURN u
        """
        params = {
            "id": usuario_id,
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "ubicacion": ubicacion,
            "experiencia": experiencia,
            "educacion": educacion,
        }
        return db.ejecutar_consulta(query, params)
    
    def consultar(self, usuario_id: str) -> Optional[Dict[str, Any]]:
        """Consulta un usuario por su ID."""
        query = """
        MATCH (u:Usuario {id: $id})
        RETURN u
        """
        resultado = db.ejecutar_consulta(query, {"id": usuario_id}, write=False)
        return resultado[0]["u"] if resultado else None
    
    def eliminar(self, usuario_id: str) -> List[Dict[str, Any]]:
        """Elimina un usuario y desconecta sus relaciones asociadas en el
        grafo."""
        query = """
        MATCH (u:Usuario {id: $id})
        DETACH DELETE u
        """
        return db.ejecutar_consulta(query, {"id": usuario_id})

    def conecta_con(self, usuario_origen_id: str, usuario_destino_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:CONECTA_CON]->(:Usuario)"""
        query = """
        MATCH (u1:Usuario {id: $u1_id})
        MATCH (u2:Usuario {id: $u2_id})
        MERGE (u1)-[r:CONECTA_CON]->(u2)
        RETURN u1, r, u2
        """
        params = {"u1_id": usuario_origen_id, "u2_id": usuario_destino_id}
        return db.ejecutar_consulta(query, params)

    def trabaja_en(self, usuario_id: str, empresa_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:TRABAJA_EN]->(:Empresa)"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (e:Empresa {id: $empresa_id})
        MERGE (u)-[r:TRABAJA_EN]->(e)
        RETURN u, r, e
        """
        params = {"usuario_id": usuario_id, "empresa_id": empresa_id}
        return db.ejecutar_consulta(query, params)

    def posee_habilidad(self, usuario_id: str, habilidad_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:POSEE]->(:Habilidad)"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (h:Habilidad {id: $habilidad_id})
        MERGE (u)-[r:POSEE]->(h)
        RETURN u, r, h
        """
        params = {"usuario_id": usuario_id, "habilidad_id": habilidad_id}
        return db.ejecutar_consulta(query, params)

    def participa_en(self, usuario_id: str, proyecto_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:PARTICIPA_EN]->(:Proyecto)"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (p:Proyecto {id: $proyecto_id})
        MERGE (u)-[r:PARTICIPA_EN]->(p)
        RETURN u, r, p
        """
        params = {"usuario_id": usuario_id, "proyecto_id": proyecto_id}
        return db.ejecutar_consulta(query, params)

    def se_postula_a(self, usuario_id: str, oferta_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:SE_POSTULA_A]->(:OfertaLaboral)"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (o:OfertaLaboral {id: $oferta_id})
        MERGE (u)-[r:SE_POSTULA_A]->(o)
        RETURN u, r, o
        """
        params = {"usuario_id": usuario_id, "oferta_id": oferta_id}
        return db.ejecutar_consulta(query, params)