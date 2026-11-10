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
        if self._driver is None:
            auth = (self._username, self._password)
            # max_connection_lifetime y keep_alive evitan el WinError 10054
            self._driver = GraphDatabase.driver(
                self._uri,
                auth=auth,
                max_connection_lifetime=60,  # Recicla conexiones viejas cada 60 seg
                max_connection_pool_size=50,
                keep_alive=True,  # Mantiene vivos los sockets TCP
            )
            self.verify_connection()

    def verify_connection(self) -> None:
        if self._driver:
            self._driver.verify_connectivity()
            print(" Conexión a Neo4j establecida correctamente.")

    def close(self) -> None:
        """Cierra el driver de Neo4j al finalizar la aplicación."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            print(" Conexión a Neo4j cerrada.")

    def ejecutar_consulta(self, query: str, parameters: Optional[Dict[str, Any]] = None, write: bool = True, ) -> List[Dict[str, Any]]:
        if self._driver is None:
            self.connect()

        routing_mode = (
            RoutingControl.WRITE if write else RoutingControl.READ
        )

        # Reintento simple si la conexión cae a mitad de transacción
        max_retries = 3
        for intento in range(max_retries):
            try:
                records, summary, keys = self._driver.execute_query(query_=query, parameters_=parameters or {}, routing_=routing_mode)
                # Formatea los resultados en una lista de diccionarios estándar
                return [record.data() for record in records]
            except Exception as e:
                if intento == max_retries - 1:
                    raise e
                print(
                    f" Reintentando consulta por reconexión ({intento + 1}/{max_retries})..."
                )
    

# Instancia global para ser reutilizada en toda la aplicación
db = DatabaseConnection()