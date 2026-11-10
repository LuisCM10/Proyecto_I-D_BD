"""
Ejecutar desde la terminal con: python consultas.py
"""

from pprint import pprint
from typing import Any, Dict, List, Optional

from conexion import db


class ConsultasGrafo:
    """Contiene consultas de lectura sobre usuarios, empresas y proyectos."""

    def __init__(self, database=None):
        # Permite reutilizar la conexión global o inyectar otra conexión en pruebas.
        self.database = database if database is not None else db

    def usuarios_con_habilidades_similares(
        self, minimo_habilidades: int = 1
    ) -> List[Dict[str, Any]]:
        """Encuentra pares de usuarios que comparten al menos N habilidades."""
        query = """
        MATCH (u1:Usuario)-[:POSEE]->(h:Habilidad)<-[:POSEE]-(u2:Usuario)
        WHERE u1.id < u2.id
        WITH u1, u2, collect(DISTINCT h.nombre) AS habilidades_comunes
        WHERE size(habilidades_comunes) >= $minimo_habilidades
        RETURN
            u1.id AS usuario1_id,
            u1.nombre AS usuario1,
            u2.id AS usuario2_id,
            u2.nombre AS usuario2,
            habilidades_comunes,
            size(habilidades_comunes) AS cantidad_habilidades
        ORDER BY cantidad_habilidades DESC, usuario1, usuario2
        """
        return self.database.ejecutar_consulta(
            query, {"minimo_habilidades": minimo_habilidades}, write=False
        )

    def contactos_en_comun(
        self, usuario1_id: str, usuario2_id: str
    ) -> List[Dict[str, Any]]:
        """Encuentra usuarios conectados con ambos profesionales."""
        query = """
        MATCH (u1:Usuario {id: $usuario1_id})-[:CONECTA_CON]-
              (contacto:Usuario)-[:CONECTA_CON]-(u2:Usuario {id: $usuario2_id})
        WHERE u1 <> u2 AND contacto <> u1 AND contacto <> u2
        RETURN DISTINCT
            contacto.id AS contacto_id,
            contacto.nombre AS contacto,
            u1.nombre AS profesional1,
            u2.nombre AS profesional2
        ORDER BY contacto
        """
        return self.database.ejecutar_consulta(
            query,
            {"usuario1_id": usuario1_id, "usuario2_id": usuario2_id},
            write=False,
        )

    def ruta_mas_corta_usuario_empresa(
        self, usuario_id: str, empresa_id: str
    ) -> Optional[Dict[str, Any]]:
        """Devuelve la ruta de menos relaciones entre un usuario y una empresa."""
        query = """
        MATCH ruta = shortestPath(
            (u:Usuario {id: $usuario_id})-[*..6]-(e:Empresa {id: $empresa_id})
        )
        RETURN
            length(ruta) AS pasos,
            [n IN nodes(ruta) | {
                tipo: head(labels(n)),
                id: toString(n.id),
                nombre: coalesce(n.nombre, n.titulo, n.`título`, '')
            }] AS recorrido,
            [rel IN relationships(ruta) | type(rel)] AS relaciones
        """
        resultados = self.database.ejecutar_consulta(
            query,
            {"usuario_id": usuario_id, "empresa_id": empresa_id},
            write=False,
        )
        return resultados[0] if resultados else None

    
    def proyectos_relacionados(self) -> List[Dict[str, Any]]:
        """Compara tecnologías (texto o nodos) y miembros en proyectos distintos."""
        query = """
        MATCH (p1:Proyecto), (p2:Proyecto)
        WHERE p1.id < p2.id
        OPTIONAL MATCH (u1:Usuario)-[:PARTICIPA_EN]->(p1)
        WITH p1, p2, collect(DISTINCT u1) AS miembros1
        OPTIONAL MATCH (u2:Usuario)-[:PARTICIPA_EN]->(p2)
        WITH p1, p2, miembros1, collect(DISTINCT u2) AS miembros2
        OPTIONAL MATCH (p1)-[:USA_TECNOLOGIA]->(t1:Tecnologia)
        WITH p1, p2, miembros1, miembros2, collect(DISTINCT t1.nombre) AS nombres1
        OPTIONAL MATCH (p2)-[:USA_TECNOLOGIA]->(t2:Tecnologia)
        WITH p1, p2, miembros1, miembros2, nombres1,
             collect(DISTINCT t2.nombre) AS nombres2
        WITH p1, p2, miembros1, miembros2,
             nombres1 + [t IN split(coalesce(p1.tecnologias, ''), ',') | trim(t)] AS tecn1,
             nombres2 + [t IN split(coalesce(p2.tecnologias, ''), ',') | trim(t)] AS tecn2
        WITH p1, p2, miembros1, miembros2,
             [t IN tecn1 WHERE t <> '' AND t IN tecn2] AS tecnologias_comunes,
             [u IN miembros1 WHERE u IN miembros2 | u.nombre] AS miembros_comunes,
             [u IN miembros1 WHERE u IS NOT NULL AND any(v IN miembros2 WHERE v IS NOT NULL AND u <> v AND EXISTS {
                MATCH (u)-[:CONECTA_CON]-(v)
             }) | u.nombre] AS miembros_conectados
        WHERE size(tecnologias_comunes) > 0
           OR size(miembros_comunes) > 0
           OR size(miembros_conectados) > 0
        RETURN p1.nombre AS proyecto1, p2.nombre AS proyecto2,
               tecnologias_comunes, miembros_comunes, miembros_conectados
        ORDER BY proyecto1, proyecto2
        """
        return self.database.ejecutar_consulta(query, write=False)

    def candidatos_recomendados(self, oferta_id: str) -> List[Dict[str, Any]]:
        """Candidatos con habilidades requeridas y proximidad a empleados."""
        query = """
        MATCH (empresa:Empresa)-[:PUBLICA]->(oferta:OfertaLaboral {id: $oferta_id})
        MATCH (oferta)-[:REQUIERE_TENER]->(h:Habilidad)<-[:POSEE]-(candidato:Usuario)
        WITH empresa, oferta, candidato, collect(DISTINCT h.nombre) AS habilidades_coincidentes
        OPTIONAL MATCH p = (candidato)-[:CONECTA_CON*1..2]-(empleado:Usuario)-[:TRABAJA_EN]->(empresa)
        WHERE candidato <> empleado
        WITH empresa, oferta, candidato, habilidades_coincidentes,
             min(length(p) - 1) AS distancia_red
        RETURN candidato.id AS candidato_id, candidato.nombre AS candidato,
               oferta.titulo AS oferta, empresa.nombre AS empresa,
               habilidades_coincidentes, size(habilidades_coincidentes) AS competencias_coincidentes,
               distancia_red
        ORDER BY competencias_coincidentes DESC, distancia_red ASC, candidato
        """
        return self.database.ejecutar_consulta(query, {"oferta_id": oferta_id}, write=False)


if __name__ == "__main__":
    consultas = ConsultasGrafo()

    try:
        resultados = consultas.proyectos_relacionados()

        for proyecto in resultados:
            pprint(proyecto)

        if not resultados:
            print("No se encontraron proyectos relacionados.")

    finally:
        consultas.database.close()