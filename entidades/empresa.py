from typing import Any, Dict, List, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id

class Empresa:

    def crear(self, nombre: str, industria: str = "", ubicacion: str = "", tamano: str = "", descripcion: str = "") -> List[Dict[str, Any]]:
        """Crea un nodo Empresa con sus propiedades: 
        (nombre, industria, ubicación, tamaño, descripción)."""
        
        empresa_id = obtener_siguiente_id(entidad="Empresa", prefijo="emp")
        
        query = """
        CREATE (e:Empresa {
            id: $id,
            nombre: $nombre,
            industria: $industria,
            ubicacion: $ubicacion,
            tamano: $tamano,
            descripcion: $descripcion
        })
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
    
    def consultar(self, empresa_id: str) -> Optional[Dict[str, Any]]:
        """Consulta una Empresa por su ID."""
        query = """
        MATCH (e:Empresa {id: $id})
        RETURN e
        """
        resultado = db.ejecutar_consulta(
            query, {"id": empresa_id}, write=False
        )
        return resultado[0]["e"] if resultado else None

    def actualizar(self, empresa_id: str, nombre: Optional[str] = None, industria: Optional[str] = None, ubicacion: Optional[str] = None, tamano: Optional[str] = None, descripcion: Optional[str] = None) -> List[Dict[str, Any]]:
        """Actualiza los campos especificados de una Empresa."""
        query = """
        MATCH (e:Empresa {id: $id})
        SET e.nombre = COALESCE($nombre, e.nombre),
            e.industria = COALESCE($industria, e.industria),
            e.ubicacion = COALESCE($ubicacion, e.ubicacion),
            e.tamano = COALESCE($tamano, e.tamano),
            e.descripcion = COALESCE($descripcion, e.descripcion)
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

    def eliminar(self, empresa_id: str) -> List[Dict[str, Any]]:
        """Elimina una Empresa y desvincula sus relaciones en el grafo."""
        query = """
        MATCH (e:Empresa {id: $id})
        DETACH DELETE e
        """
        return db.ejecutar_consulta(query, {"id": empresa_id})

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
    
    def desvincular_publica(self, empresa_id: str, oferta_id: str) -> List[Dict[str, Any]]:
        """Elimina la relación: (:Empresa)-[:PUBLICA]->(:OfertaLaboral)"""
        query = """
        MATCH (e:Empresa {id: $e_id})-[r:PUBLICA]->(o:OfertaLaboral {id: $o_id})
        DELETE r
        """
        params = {"e_id": empresa_id, "o_id": oferta_id}
        return db.ejecutar_consulta(query, params)

    def desvincular_tiene_proyecto(self, empresa_id: str, proyecto_id: str) -> List[Dict[str, Any]]:
        """Elimina la relación: (:Empresa)-[:TIENE]->(:Proyecto)"""
        query = """
        MATCH (e:Empresa {id: $e_id})-[r:TIENE]->(p:Proyecto {id: $p_id})
        DELETE r
        """
        params = {"e_id": empresa_id, "p_id": proyecto_id}
        return db.ejecutar_consulta(query, params)