from typing import List, Dict, Any
from conexion import db

class CaminosYConexiones:
    def consultar_camino_entre_usuarios(self, usuario1_id: str, usuario2_id: str) -> List[Dict[str, Any]]:
        """
        Encuentra el camino más corto de conexiones profesionales entre dos usuarios.
        """
        query = """
        MATCH p = shortestPath(
            (u1:Usuario {id: $u1_id})-[:CONECTA_CON*..6]-(u2:Usuario {id: $u2_id})
        )
        RETURN [node IN nodes(p) | {id: node.id, nombre: node.nombre, label: labels(node)[0]}] AS camino,
               length(p) AS grados_de_separacion
        """
        return db.ejecutar_consulta(query, {"u1_id": usuario1_id, "u2_id": usuario2_id}, write=False)

    def consultar_camino_usuario_a_empresa(self, usuario_id: str, empresa_id: str) -> List[Dict[str, Any]]:
        """
        Encuentra cómo un usuario está conectado con una empresa a través de su red
        (contactos que trabajan allí, ofertas a las que aplicó, etc.).
        """
        query = """
        MATCH p = shortestPath(
            (u:Usuario {id: $u_id})-[*..4]-(e:Empresa {id: $e_id})
        )
        RETURN [node IN nodes(p) | {id: node.id, nombre: coalesce(node.nombre, node.titulo), tipo: labels(node)[0]}] AS camino,
               length(p) AS distancia
        """
        return db.ejecutar_consulta(query, {"u_id": usuario_id, "e_id": empresa_id}, write=False)

    def consultar_camino_usuario_a_oferta(self, usuario_id: str, oferta_id: str) -> List[Dict[str, Any]]:
        """
        Muestra la conexión entre un usuario y una oferta (habilidades compartidas o contactos en la empresa).
        """
        query = """
        MATCH p = shortestPath(
            (u:Usuario {id: $u_id})-[*..4]-(o:OfertaLaboral {id: $o_id})
        )
        RETURN [node IN nodes(p) | {id: node.id, nombre: coalesce(node.nombre, node.titulo), tipo: labels(node)[0]}] AS camino,
               [rel IN relationships(p) | type(rel)] AS relaciones
        """
        return db.ejecutar_consulta(query, {"u_id": usuario_id, "o_id": oferta_id}, write=False)

    
