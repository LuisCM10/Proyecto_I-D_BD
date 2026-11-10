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
        MATCH (u1:Usuario)-[:TIENE]->(h:Habilidad)<-[:TIENE]-(u2:Usuario)
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
        """Consulta proyectos que comparten tecnologías o miembros relacionados."""

        query = """
        MATCH (p1:Proyecto), (p2:Proyecto)
        WHERE p1.id < p2.id

        OPTIONAL MATCH (u1:Usuario)-[:PARTICIPA_EN]->(p1)
        WITH p1, p2, collect(DISTINCT u1) AS miembros1

        OPTIONAL MATCH (u2:Usuario)-[:PARTICIPA_EN]->(p2)
        WITH p1, p2, miembros1,
             collect(DISTINCT u2) AS miembros2

        WITH p1, p2, miembros1, miembros2,
             [t IN coalesce(p1.tecnologias, [])
              WHERE t IN coalesce(p2.tecnologias, [])]
              AS tecnologias_comunes,
             [u IN miembros1 WHERE u IN miembros2 | u.nombre]
              AS miembros_comunes

        WITH p1, p2, tecnologias_comunes, miembros_comunes,
             [u1 IN miembros1 |
                 [u2 IN miembros2
                  WHERE u1 <> u2 AND EXISTS {
                      MATCH (u1)-[:CONECTA_CON]-(u2)
                  }
                  | u1.nombre + ' - ' + u2.nombre]
             ] AS conexiones

        WITH p1, p2, tecnologias_comunes, miembros_comunes,
             reduce(lista = [], grupo IN conexiones |
                 lista + grupo) AS miembros_conectados

        WHERE size(tecnologias_comunes) > 0
           OR size(miembros_comunes) > 0
           OR size(miembros_conectados) > 0

        RETURN
            p1.nombre AS proyecto1,
            p2.nombre AS proyecto2,
            tecnologias_comunes,
            miembros_comunes,
            miembros_conectados
        ORDER BY proyecto1, proyecto2
        """

        return self.database.ejecutar_consulta(
            query, write=False
        )



def candidatos_recomendados(
    self, oferta_id: str
) -> List[Dict[str, Any]]:
    """Busca candidatos con habilidades requeridas y conexiones
    con empleados de la empresa que publicó la oferta.
    """

    query = """
    MATCH (empresa:Empresa)-[:PUBLICA]->(oferta:OfertaLaboral {id: $oferta_id})
    MATCH (candidato:Usuario)-[conexiones:CONECTA_CON*1..2]-
          (empleado:Usuario)-[:TRABAJA_EN]->(empresa)
    MATCH (oferta)-[:REQUIERE_TENER]->(h:Habilidad)<-[:TIENE]-(candidato)
    WITH
        candidato,
        oferta,
        empresa,
        count(DISTINCT h) AS competencias_coincidentes,
        collect(DISTINCT h.nombre) AS habilidades_coincidentes,
        min(size(conexiones)) AS distancia_red
    RETURN
        candidato.id AS candidato_id,
        candidato.nombre AS candidato,
        coalesce(oferta.titulo, oferta.`título`, '') AS oferta,
        empresa.nombre AS empresa,
        habilidades_coincidentes,
        competencias_coincidentes,
        distancia_red
    ORDER BY competencias_coincidentes DESC, distancia_red ASC, candidato
    """

    return self.database.ejecutar_consulta(
        query,
        {"oferta_id": oferta_id},
        write=False
    )


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