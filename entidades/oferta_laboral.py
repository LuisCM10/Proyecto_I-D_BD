from typing import Any, Dict, List
from conexion import db


class OfertaLaboral:

    def crear(self, oferta_id: str, titulo: str, descripcion: str = "", fecha_publicacion: str = "", fecha_cierre: str = "", ubicacion: str = "", salario: float = 0.0, tipo_contrato: str = "") -> List[Dict[str, Any]]:
        """Crea o actualiza un nodo OfertaLaboral con sus propiedades:
        (título, descripción, fecha_publicación, fecha_cierre, ubicación, salario, tipo_contrato).
        """
        query = """
        MERGE (o:OfertaLaboral {id: $id})
        ON CREATE SET 
            o.titulo = $titulo,
            o.descripcion = $descripcion,
            o.fecha_publicacion = $fecha_publicacion,
            o.fecha_cierre = $fecha_cierre,
            o.ubicacion = $ubicacion,
            o.salario = $salario,
            o.tipo_contrato = $tipo_contrato
        ON MATCH SET 
            o.titulo = $titulo,
            o.descripcion = $descripcion,
            o.fecha_publicacion = $fecha_publicacion,
            o.fecha_cierre = $fecha_cierre,
            o.ubicacion = $ubicacion,
            o.salario = $salario,
            o.tipo_contrato = $tipo_contrato
        RETURN o
        """
        params = {
            "id": oferta_id,
            "titulo": titulo,
            "descripcion": descripcion,
            "fecha_publicacion": fecha_publicacion,
            "fecha_cierre": fecha_cierre,
            "ubicacion": ubicacion,
            "salario": salario,
            "tipo_contrato": tipo_contrato,
        }
        return db.ejecutar_consulta(query, params)

    def requiere_tener(self, oferta_id: str, habilidad_id: str) -> List[Dict[str, Any]]:
        """Crea la relación: (:OfertaLaboral)-[:REQUIERE_TENER]->(:Habilidad)"""
        query = """
        MATCH (o:OfertaLaboral {id: $oferta_id})
        MATCH (h:Habilidad {id: $habilidad_id})
        MERGE (o)-[r:REQUIERE_TENER]->(h)
        RETURN o, r, h
        """
        params = {"oferta_id": oferta_id, "habilidad_id": habilidad_id}
        return db.ejecutar_consulta(query, params)