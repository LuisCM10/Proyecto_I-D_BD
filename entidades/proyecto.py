from typing import Any, Dict, List, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id

class Proyecto:

    def crear(self, nombre: str, descripcion: str = "", fecha_inicio: str = "", fecha_fin: str = "", tecnologias: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Crea un nodo Proyecto con sus propiedades:
        (nombre, descripción, fecha_inicio, fecha_fin, tecnologías).
        """
        proyecto_id = obtener_siguiente_id(entidad="Proyecto", prefijo="proy")
        query = """
        CREATE (p:Proyecto {
            id: $id,
            nombre: $nombre,
            descripcion: $descripcion,
            fecha_inicio: $fecha_inicio,
            fecha_fin: $fecha_fin,
        })
        RETURN p
        """
        params = {
            "id": proyecto_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
        }
        return db.ejecutar_consulta(query, params)
    
    def consultar(self, proyecto_id: str) -> Optional[Dict[str, Any]]:
        """Consulta un Proyecto por su ID."""
        query = """
        MATCH (p:Proyecto {id: $id})
        RETURN p
        """
        resultado = db.ejecutar_consulta(
            query, {"id": proyecto_id}, write=False
        )
        return resultado[0]["p"] if resultado else None

    def actualizar(self, proyecto_id: str, nombre: Optional[str] = None, descripcion: Optional[str] = None, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, tecnologias: Optional[str] = None) -> List[Dict[str, Any]]:
        """Actualiza los campos especificados de un Proyecto."""
        query = """
        MATCH (p:Proyecto {id: $id})
        SET p.nombre = COALESCE($nombre, p.nombre),
            p.descripcion = COALESCE($descripcion, p.descripcion),
            p.fecha_inicio = COALESCE($fecha_inicio, p.fecha_inicio),
            p.fecha_fin = COALESCE($fecha_fin, p.fecha_fin)
        RETURN p
        """
        params = {
            "id": proyecto_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
        return db.ejecutar_consulta(query, params)

    def eliminar(self, proyecto_id: str) -> List[Dict[str, Any]]:
        """Elimina un Proyecto y desvincula sus relaciones en el grafo."""
        query = """
        MATCH (p:Proyecto {id: $id})
        DETACH DELETE p
        """
        return db.ejecutar_consulta(query, {"id": proyecto_id})
    
    def usa_tecnologia(
            self,
            proyecto_id: str,
            tecnologia_id: str
        ) -> List[Dict[str, Any]]:
            """Crea la relación: (:Proyecto)-[:USA_TECNOLOGIA]->(:Tecnologia)"""
            query = """
            MATCH (p:Proyecto {id: $proyecto_id})
            MATCH (t:Tecnologia {id: $tecnologia_id})
            MERGE (p)-[r:USA_TECNOLOGIA]->(t)
            RETURN p, r, t
            """
            params = {
                "proyecto_id": proyecto_id,
                "tecnologia_id": tecnologia_id
            }
            return db.ejecutar_consulta(query, params)
    
    def desvincular_tecnologia(
            self,
            proyecto_id: str,
            tecnologia_id: str
        ) -> List[Dict[str, Any]]:
            """Elimina la relación: (:Proyecto)-[:USA_TECNOLOGIA]->(:Tecnologia)"""
            query = """
            MATCH (p:Proyecto {id: $proyecto_id})-[r:USA_TECNOLOGIA]->(t:Tecnologia {id: $tecnologia_id})
            DELETE r
            """
            params = {
                "proyecto_id": proyecto_id,
                "tecnologia_id": tecnologia_id
            }
            return db.ejecutar_consulta(query, params)