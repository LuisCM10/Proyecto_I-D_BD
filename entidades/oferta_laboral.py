from typing import Any, Dict, List, Optional
from conexion import db
from entidades.controller import obtener_siguiente_id

class OfertaLaboral:

    def crear(self, titulo: str, descripcion: str = "", fecha_publicacion: str = "", fecha_cierre: str = "", ubicacion: str = "", salario: float = 0.0, tipo_contrato: str = "") -> List[Dict[str, Any]]:
        """Crea un nodo OfertaLaboral con sus propiedades:
        (título, descripción, fecha_publicación, fecha_cierre, ubicación, salario, tipo_contrato).
        """
        oferta_id = obtener_siguiente_id(entidad="OfertaLaboral", prefijo="ofe")
        query = """
        CREATE (o:OfertaLaboral {
            id: $id,
            titulo: $titulo,
            descripcion: $descripcion,
            fecha_publicacion: $fecha_publicacion,
            fecha_cierre: $fecha_cierre,
            ubicacion: $ubicacion,
            salario: $salario,
            tipo_contrato: $tipo_contrato
        })
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
    
    def consultar(self, oferta_id: str) -> Optional[Dict[str, Any]]:
        """Consulta una Oferta Laboral por su ID."""
        query = """
        MATCH (o:OfertaLaboral {id: $id})
        RETURN o
        """
        resultado = db.ejecutar_consulta(
            query, {"id": oferta_id}, write=False
        )
        return resultado[0]["o"] if resultado else None

    def actualizar(self, oferta_id: str, titulo: Optional[str] = None, descripcion: Optional[str] = None, fecha_publicacion: Optional[str] = None, fecha_cierre: Optional[str] = None, ubicacion: Optional[str] = None, salario: Optional[float] = None, tipo_contrato: Optional[str] = None) -> List[Dict[str, Any]]:
        """Actualiza los campos especificados de una Oferta Laboral."""
        query = """
        MATCH (o:OfertaLaboral {id: $id})
        SET o.titulo = COALESCE($titulo, o.titulo),
            o.descripcion = COALESCE($descripcion, o.descripcion),
            o.fecha_publicacion = COALESCE($fecha_publicacion, o.fecha_publicacion),
            o.fecha_cierre = COALESCE($fecha_cierre, o.fecha_cierre),
            o.ubicacion = COALESCE($ubicacion, o.ubicacion),
            o.salario = COALESCE($salario, o.salario),
            o.tipo_contrato = COALESCE($tipo_contrato, o.tipo_contrato)
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

    def eliminar(self, oferta_id: str) -> List[Dict[str, Any]]:
        """Elimina una Oferta Laboral y desvincula sus relaciones en el grafo."""
        query = """
        MATCH (o:OfertaLaboral {id: $id})
        DETACH DELETE o
        """
        return db.ejecutar_consulta(query, {"id": oferta_id})

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