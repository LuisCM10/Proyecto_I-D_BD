from conexion import db

def crear_restricciones_unicidad():
        """Crea las restricciones de unicidad en Neo4j para asegurar que no existan

        IDs duplicados en ninguna entidad.
        """
        restricciones = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Empresa) REQUIRE e.id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Habilidad) REQUIRE h.id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Proyecto) REQUIRE p.id IS UNIQUE;",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (o:OfertaLaboral) REQUIRE o.id IS UNIQUE;",
        ]

        print(" Creando restricciones de unicidad en Neo4j...")
        for query in restricciones:
            db.ejecutar_consulta(query)
        print(" Restricciones de unicidad aplicadas correctamente.")
        
def obtener_siguiente_id(entidad: str, prefijo: str) -> str:
    """Incrementa atómicamente el contador centralizado en Neo4j y retorna el ID

    formateado.

    :param entidad: El nombre del Label (ej: 'Usuario', 'Empresa', 'Proyecto',
    'Habilidad', 'OfertaLaboral')
    :param prefijo: El prefijo para el ID (ej: 'usr', 'emp', 'proy', 'hab',
    'ofe')
    :return: String con el ID autoincrementado (ej: 'usr_1', 'usr_2', 'emp_1')
    """
    query = """
    MERGE (c:Contador {entidad: $entidad})
    ON CREATE SET c.ultimo_id = 0
    SET c.ultimo_id = c.ultimo_id + 1
    RETURN c.ultimo_id AS siguiente_num
    """
    resultado = db.ejecutar_consulta(query, {"entidad": entidad})
    siguiente_num = resultado[0]["siguiente_num"]
    return f"{prefijo}_{siguiente_num}"