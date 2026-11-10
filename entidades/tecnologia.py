from typing import List, Dict, Any, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id

class Tecnologia:
    def crear(self, nombre: str, categoria: str = "", descripcion: str = "") -> List[Dict[str, Any]]:
        """Crea una entidad Tecnologia. propiedades: id, nombre, categoria, descripcion"""
        t_id = obtener_siguiente_id("Tecnologia", "tec")
        query = """
        CREATE (t:Tecnologia {
            id: $id,
            nombre: $nombre,
            categoria: $categoria,
            descripcion: $descripcion
        })
        RETURN t
        """
        params = {
            "id": t_id,
            "nombre": nombre,
            "categoria": categoria,
            "descripcion": descripcion
        }
        return db.ejecutar_consulta(query, params)

    def consultar(self, tecnologia_id: str) -> Optional[Dict[str, Any]]:
        """Consulta una Tecnologia por su ID."""
        query = """
        MATCH (t:Tecnologia {id: $id})
        RETURN t
        """
        resultado = db.ejecutar_consulta(query, {"id": tecnologia_id}, write=False)
        return resultado[0]["t"] if resultado else None

    def actualizar(
        self,
        tecnologia_id: str,
        nombre: Optional[str] = None,
        categoria: Optional[str] = None,
        descripcion: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Actualiza las propiedades de una Tecnologia."""
        query = """
        MATCH (t:Tecnologia {id: $id})
        SET t.nombre = COALESCE($nombre, t.nombre),
            t.categoria = COALESCE($categoria, t.categoria),
            t.descripcion = COALESCE($descripcion, t.descripcion)
        RETURN t
        """
        params = {
            "id": tecnologia_id,
            "nombre": nombre,
            "categoria": categoria,
            "descripcion": descripcion
        }
        return db.ejecutar_consulta(query, params)

    def eliminar(self, tecnologia_id: str) -> List[Dict[str, Any]]:
        """Elimina una Tecnologia y sus relaciones en el grafo."""
        query = """
        MATCH (t:Tecnologia {id: $id})
        DETACH DELETE t
        """
        return db.ejecutar_consulta(query, {"id": tecnologia_id})

