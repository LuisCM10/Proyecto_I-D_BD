from typing import Any, Dict, List
from conexion import db


class Usuario:

    def crear(self, usuario_id: str, nombre: str, correo: str, telefono: str = "", ubicacion: str = "", experiencia: str = "", educacion: str = "") -> List[Dict[str, Any]]:
        """Crea o actualiza un nodo Usuario con sus propiedades: (nombre, correo, teléfono, ubicación, experiencia, educación)."""
        query = """
        MERGE (u:Usuario {id: $id})
        ON CREATE SET 
            u.nombre = $nombre,
            u.correo = $correo,
            u.telefono = $telefono,
            u.ubicacion = $ubicacion,
            u.experiencia = $experiencia,
            u.educacion = $educacion
        ON MATCH SET 
            u.nombre = $nombre,
            u.correo = $correo,
            u.telefono = $telefono,
            u.ubicacion = $ubicacion,
            u.experiencia = $experiencia,
            u.educacion = $educacion
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

    def tiene_habilidad(self, usuario_id: str, habilidad_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Usuario)-[:TIENE]->(:Habilidad)"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (h:Habilidad {id: $habilidad_id})
        MERGE (u)-[r:TIENE]->(h)
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