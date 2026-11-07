import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase, RoutingControl

load_dotenv()


class DatabaseConnection:
    """Maneja la conexión a Neo4j.

   Es utilizada por otras clases para establer conexion y enviar consultas a la base de datos.
    """

    def __init__(self):
        self._uri = os.getenv("NEO4J_URI")
        self._username = os.getenv("NEO4J_USERNAME")
        self._password = os.getenv("NEO4J_PASSWORD")
        self._driver: Optional[Driver] = None

    def connect(self) -> None:
        """Inicializa el driver y verifica la conectividad con la base de
        datos."""
        if self._driver is None:
            auth = (self._username, self._password)
            self._driver = GraphDatabase.driver(self._uri, auth=auth)
            self.verify_connection()

    def verify_connection(self) -> None:
        """Verifica que las credenciales y la URL sean válidas."""
        if self._driver:
            self._driver.verify_connectivity()
            print(" Conexión a Neo4j establecida correctamente.")

    def close(self) -> None:
        """Cierra el driver de Neo4j al finalizar la aplicación."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            print(" Conexión a Neo4j cerrada.")

    def ejecutar_consulta(self, query: str, parameters: Optional[Dict[str, Any]] = None, write: bool = True,) -> List[Dict[str, Any]]:
        """Ejecuta una consulta Cypher y retorna los resultados como una lista
        de diccionarios.

        :param query: Consulta en Cypher a ejecutar.
        :param parameters: Diccionario con los parámetros de la consulta.
        :param write: True si modifica la base de datos (CREATE, MERGE, DELETE),
                      False para consultas de solo lectura (MATCH).
        :return: Lista de registros mapeados como diccionario Python.
        """
        if self._driver is None:
            self.connect()

        routing_mode = (
            RoutingControl.WRITE if write else RoutingControl.READ
        )
        records, summary, keys = self._driver.execute_query(query_=query, parameters_=parameters or {}, routing_=routing_mode)

        # Formatea los resultados en una lista de diccionarios estándar
        return [record.data() for record in records]
    

# Instancia global para ser reutilizada en toda la aplicación
db = DatabaseConnection()