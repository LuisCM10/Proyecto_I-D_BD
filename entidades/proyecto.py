from typing import Any, Dict, List, Optional
from conexion import db


class Proyecto:

    def crear(self, proyecto_id: str, nombre: str, descripcion: str = "", fecha_inicio: str = "", fecha_fin: str = "", tecnologias: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Crea o actualiza un nodo Proyecto con sus propiedades:
        (nombre, descripción, fecha_inicio, fecha_fin, tecnologías).
        """
        query = """
        MERGE (p:Proyecto {id: $id})
        ON CREATE SET 
            p.nombre = $nombre,
            p.descripcion = $descripcion,
            p.fecha_inicio = $fecha_inicio,
            p.fecha_fin = $fecha_fin,
            p.tecnologias = $tecnologias
        ON MATCH SET 
            p.nombre = $nombre,
            p.descripcion = $descripcion,
            p.fecha_inicio = $fecha_inicio,
            p.fecha_fin = $fecha_fin,
            p.tecnologias = $tecnologias
        RETURN p
        """
        params = {
            "id": proyecto_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "tecnologias": tecnologias or [],
        }
        return db.ejecutar_consulta(query, params)