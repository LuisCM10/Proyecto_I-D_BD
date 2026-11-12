from typing import List, Dict, Any
from conexion import db

class SistemaRecomendacion:
    def recomendar_contactos(self, usuario_id: str, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Recomienda 'Amigos de mis amigos' (contactos de segundo grado) con los que aún no hay conexión directas,
        ordenados por la cantidad de amigos en común.
        """
        query = """
        MATCH (u:Usuario {id: $u_id})-[:CONECTA_CON]-(amigo:Usuario)-[:CONECTA_CON]-(recomendado:Usuario)
        WHERE u <> recomendado AND NOT (u)-[:CONECTA_CON]-(recomendado)
        RETURN recomendado.id AS id, 
                recomendado.nombre AS nombre, 
                recomendado.correo AS correo,
                count(DISTINCT amigo) AS amigos_en_comun
        ORDER BY amigos_en_comun DESC
        LIMIT $limite
        """
        return db.ejecutar_consulta(query, {"u_id": usuario_id, "limite": limite}, write=False)

    def recomendar_empleos(self, usuario_id: str, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Recomienda ofertas laborales basadas en el match de habilidades que el usuario posee
        y que la oferta requiere.
        """
        query = """
        MATCH (u:Usuario {id: $u_id})-[:POSEE]->(h:Habilidad)<-[:REQUIERE_TENER]-(o:OfertaLaboral)<-[:PUBLICA]-(e:Empresa)
        WHERE NOT EXISTS { MATCH (u)-[:SE_POSTULA_A]->(o) }
          AND coalesce(o.estado, 'Abierta') = 'Abierta'
          AND (o.fecha_cierre IS NULL OR toString(o.fecha_cierre) >= toString(date()))
        WITH o, e, count(h) AS habilidades_coincidentes, collect(h.nombre) AS habilidades_match
        RETURN o.id AS oferta_id,
                o.titulo AS titulo_oferta,
                o.salario AS salario,
                e.nombre AS empresa,
                habilidades_coincidentes,
                habilidades_match
        ORDER BY habilidades_coincidentes DESC
        LIMIT $limite
        """
        return db.ejecutar_consulta(query, {"u_id": usuario_id, "limite": limite}, write=False)

    def recomendar_colaboradores_para_proyecto(self, proyecto_id: str, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Recomienda usuarios calificados para un proyecto basándose en si trabajan en la empresa dueña
        del proyecto o si tienen habilidades afines al proyecto.
        """
        query = """
        MATCH (e:Empresa)-[:TIENE]->(p:Proyecto {id: $p_id})
        MATCH (u:Usuario)
        WHERE NOT (u)-[:PARTICIPA_EN]->(p)
        OPTIONAL MATCH (u)-[:TRABAJA_EN]->(e)
        OPTIONAL MATCH (u)-[:POSEE]->(h:Habilidad)
        WITH u, count(DISTINCT h) AS num_habilidades, count(e) AS pertenece_a_empresa
        RETURN u.id AS usuario_id,
                u.nombre AS nombre,
                u.experiencia AS experiencia,
                (num_habilidades + (pertenece_a_empresa * 3)) AS puntaje_relevancia
        ORDER BY puntaje_relevancia DESC
        LIMIT $limite
        """
        return db.ejecutar_consulta(query, {"p_id": proyecto_id, "limite": limite}, write=False)