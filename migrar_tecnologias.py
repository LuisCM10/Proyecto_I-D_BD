from conexion import db
from entidades.tecnologia import Tecnologia
from entidades.proyecto import Proyecto

def migrar_y_poblar_tecnologias():
    """
    1. Asegura restricción de unicidad para la nueva entidad Tecnología.
    2. Extrae las tecnologías de la propiedad 'tecnologias' de los Proyectos existentes.
    3. Crea los nodos :Tecnologia.
    4. Crea las relaciones (:Proyecto)-[:USA_TECNOLOGIA]->(:Tecnologia).
    5. Elimina (REMOVE) la propiedad 'tecnologias' de todos los nodos :Proyecto.
    """
    print("--- 1. Creando restricción de unicidad para Tecnología ---")
    db.ejecutar_consulta("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tecnologia) REQUIRE t.id IS UNIQUE;")
    print("✓ Restricción creada correctamente.")

    repo_tec = Tecnologia()

    # Mapa de tecnologías identificadas con sus detalles
    tecnologias_catalogo = {
        "Python": {"categoria": "Lenguaje de Programación", "descripcion": "Lenguaje multipropósito de alto nivel."},
        "Neo4j": {"categoria": "Base de Datos", "descripcion": "Base de datos orientada a grafos."},
        "Cypher": {"categoria": "Lenguaje de Consulta", "descripcion": "Lenguaje declarativo para grafos Neo4j."},
        "FastAPI": {"categoria": "Framework Backend", "descripcion": "Framework moderno en Python para construir APIs."},
        "Nios II Assembly": {"categoria": "Lenguaje Ensamblador", "descripcion": "Arquitectura de procesador embebido Nios II."},
        "VHDL": {"categoria": "Hardware Description Language", "descripcion": "Lenguaje de descripción de hardware para FPGAs."},
        "C": {"categoria": "Lenguaje de Programación", "descripcion": "Lenguaje estructurado de bajo/medio nivel."},
        "PostgreSQL": {"categoria": "Base de Datos", "descripcion": "Sistema de base de datos relacional orientada a objetos."},
        "SQLAlchemy": {"categoria": "ORM", "descripcion": "Toolbox ORM de Python para mapeo relacional."}
    }

    print("--- 2. Creando Nodos de Tecnología ---")
    mapa_tec_ids = {}
    for nombre_tec, info in tecnologias_catalogo.items():
        
        nuevo = repo_tec.crear(nombre=nombre_tec, categoria=info["categoria"], descripcion=info["descripcion"])
        mapa_tec_ids[nombre_tec] = nuevo[0]["t"]["id"]  # Guardar el ID generado
        print(f"  - Tecnología '{nombre_tec}' creada con ID: {nuevo[0]['t']['id']}")

    print("--- 3. Mapeando y Creando Relaciones desde Proyectos ---")
    # Obtener proyectos con su propiedad de tecnologías
    proyectos = db.ejecutar_consulta("MATCH (p:Proyecto) RETURN p.id AS id, p.nombre AS nombre, p.tecnologias AS tecnologias", write=False)
    proyecto = Proyecto()
    for p in proyectos:
        p_id = p["id"]
        tec_str = p.get("tecnologias")
        if tec_str:
            # Separar por comas
            nombres_tec = [t.strip() for t in tec_str.split(",")]
            for nombre_tec in nombres_tec:
                if nombre_tec in mapa_tec_ids:
                    t_id = mapa_tec_ids[nombre_tec]
                    proyecto.usa_tecnologia(p_id, t_id)
                    print(f"  - Vinculado Proyecto ({p_id}) -> [:USA_TECNOLOGIA] -> Tecnología '{nombre_tec}' ({t_id})")

    print("--- 4. Eliminando propiedad 'tecnologias' de la entidad Proyecto ---")
    query_eliminar_prop = "MATCH (p:Proyecto) REMOVE p.tecnologias RETURN count(p) AS proyectos_actualizados"
    res = db.ejecutar_consulta(query_eliminar_prop)
    proyectos_afectados = res[0]["proyectos_actualizados"] if res else 0
    print(f"✓ Propiedad 'tecnologias' eliminada exitosamente de {proyectos_afectados} nodo(s) Proyecto.")

    print(" Migración completada con éxito.")

if __name__ == "__main__":
    migrar_y_poblar_tecnologias()
