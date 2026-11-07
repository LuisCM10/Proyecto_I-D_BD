from typing import Any, Dict, List
from conexion import db


class Habilidad:

    def crear(self, habilidad_id: str, nombre: str,  categoria: str = "", nivel: str = "") -> List[Dict[str, Any]]:
        """Crea o actualiza un nodo Habilidad con sus propiedades: (nombre, categoría, nivel).
        """
        query = """
        MERGE (h:Habilidad {id: $id})
        ON CREATE SET 
            h.nombre = $nombre,
            h.categoria = $categoria,
            h.nivel = $nivel
        ON MATCH SET 
            h.nombre = $nombre,
            h.categoria = $categoria,
            h.nivel = $nivel
        RETURN h
        """
        params = {
            "id": habilidad_id,
            "nombre": nombre,
            "categoria": categoria,
            "nivel": nivel,
        }
        return db.ejecutar_consulta(query, params)