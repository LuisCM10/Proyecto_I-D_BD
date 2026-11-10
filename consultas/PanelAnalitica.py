from typing import List, Dict, Any
from conexion import db

class PanelAnalitica:
    def obtener_usuarios_mas_influyentes(self, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Calcula el Grado de Centralidad (Degree Centrality) de los usuarios (número de conexiones profesionales).
        """
        query = """
        MATCH (u:Usuario)
        OPTIONAL MATCH (u)-[r:CONECTA_CON]-(:Usuario)
        WITH u, count(r) AS conexiones
        RETURN u.id AS id, u.nombre AS nombre, u.correo AS correo, conexiones
        ORDER BY conexiones DESC
        LIMIT $limite
        """
        return db.ejecutar_consulta(query, {"limite": limite}, write=False)

    def obtener_habilidades_mas_demandadas(self, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Identifica las habilidades más requeridas en el mercado según las ofertas laborales publicadas.
        """
        query = """
        MATCH (h:Habilidad)<-[:REQUIERE_TENER]-(o:OfertaLaboral)
        RETURN h.id AS habilidad_id,
               h.nombre AS habilidad,
               h.categoria AS categoria,
               count(o) AS demanda_ofertas
        ORDER BY demanda_ofertas DESC
        LIMIT $limite
        """
        return db.ejecutar_consulta(query, {"limite": limite}, write=False)

    def detectar_comunidades_por_empresa(self) -> List[Dict[str, Any]]:
        """
        Detecta agrupaciones/comunidades de usuarios que pertenecen a la misma empresa y comparten proyectos.
        """
        query = """
        MATCH (e:Empresa)<-[:TRABAJA_EN]-(u:Usuario)
        OPTIONAL MATCH (u)-[:PARTICIPA_EN]->(p:Proyecto)<-[:TIENE]-(e)
        RETURN e.nombre AS empresa,
               count(DISTINCT u) AS total_miembros,
               collect(DISTINCT u.nombre) AS miembros,
               collect(DISTINCT p.nombre) AS proyectos_compartidos
        ORDER BY total_miembros DESC
        """
        return db.ejecutar_consulta(query, write=False)