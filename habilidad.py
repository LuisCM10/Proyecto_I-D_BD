from typing import Any, Dict, List, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id

class Habilidad:

    def crear(self, nombre: str,  categoria: str = "", nivel: str = "") -> List[Dict[str, Any]]:
        """Crea un nodo Habilidad con sus propiedades: 
        (nombre, categoría, nivel).
        """
        habilidad_id = obtener_siguiente_id(entidad="Habilidad", prefijo="hab")
        query = """
        CREATE (h:Habilidad {
            id: $id,
            nombre: $nombre,
            categoria: $categoria,
            nivel: $nivel
        })
        RETURN h
        """
        params = {
            "id": habilidad_id,
            "nombre": nombre,
            "categoria": categoria,
            "nivel": nivel,
        }
        return db.ejecutar_consulta(query, params)
    
    def consultar(self, habilidad_id: str) -> Optional[Dict[str, Any]]:
        """Consulta una Habilidad por su ID."""
        query = """
        MATCH (h:Habilidad {id: $id})
        RETURN h
        """
        resultado = db.ejecutar_consulta(
            query, {"id": habilidad_id}, write=False
        )
        return resultado[0]["h"] if resultado else None

    def actualizar(self, habilidad_id: str, nombre: Optional[str] = None, categoria: Optional[str] = None, nivel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Actualiza los campos especificados de una Habilidad."""
        query = """
        MATCH (h:Habilidad {id: $id})
        SET h.nombre = COALESCE($nombre, h.nombre),
            h.categoria = COALESCE($categoria, h.categoria),
            h.nivel = COALESCE($nivel, h.nivel)
        RETURN h
        """
        params = {
            "id": habilidad_id,
            "nombre": nombre,
            "categoria": categoria,
            "nivel": nivel,
        }
        return db.ejecutar_consulta(query, params)

    def eliminar(self, habilidad_id: str) -> List[Dict[str, Any]]:
        """Elimina una Habilidad y desvincula sus relaciones en el grafo."""
        query = """
        MATCH (h:Habilidad {id: $id})
        DETACH DELETE h
        """
        return db.ejecutar_consulta(query, {"id": habilidad_id})