from typing import Any, Dict, List
from conexion import db


class Empresa:

    def crear(self, empresa_id: str, nombre: str, industria: str = "", ubicacion: str = "", tamano: str = "", descripcion: str = "") -> List[Dict[str, Any]]:
        """Crea o actualiza un nodo Empresa con sus propiedades: 
        (nombre, industria, ubicación, tamaño, descripción)."""
        query = """
        MERGE (e:Empresa {id: $id})
        ON CREATE SET 
            e.nombre = $nombre,
            e.industria = $industria,
            e.ubicacion = $ubicacion,
            e.tamano = $tamano,
            e.descripcion = $descripcion
        ON MATCH SET 
            e.nombre = $nombre,
            e.industria = $industria,
            e.ubicacion = $ubicacion,
            e.tamano = $tamano,
            e.descripcion = $descripcion
        RETURN e
        """
        params = {
            "id": empresa_id,
            "nombre": nombre,
            "industria": industria,
            "ubicacion": ubicacion,
            "tamano": tamano,
            "descripcion": descripcion,
        }
        return db.ejecutar_consulta(query, params)

    def publica_oferta(self, empresa_id: str, oferta_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Empresa)-[:PUBLICA]->(:OfertaLaboral)"""
        query = """
        MATCH (e:Empresa {id: $empresa_id})
        MATCH (o:OfertaLaboral {id: $oferta_id})
        MERGE (e)-[r:PUBLICA]->(o)
        RETURN e, r, o
        """
        params = {"empresa_id": empresa_id, "oferta_id": oferta_id}
        return db.ejecutar_consulta(query, params)

    def tiene_proyecto(self, empresa_id: str, proyecto_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:Empresa)-[:TIENE]->(:Proyecto)"""
        query = """
        MATCH (e:Empresa {id: $empresa_id})
        MATCH (p:Proyecto {id: $proyecto_id})
        MERGE (e)-[r:TIENE]->(p)
        RETURN e, r, p
        """
        params = {"empresa_id": empresa_id, "proyecto_id": proyecto_id}
        return db.ejecutar_consulta(query, params)