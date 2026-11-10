from entidades.usuario import Usuario
from entidades.empresa import Empresa


# Instanciar el repositorio
repo_usuario = Usuario()
repo_empresa = Empresa()

    
from conexion import db


def vaciar_base_datos() -> None:
    """Elimina todos los nodos y relaciones existentes en la base de datos de

    Neo4j.
    """
    query = "MATCH (n) DETACH DELETE n"

    print(" Eliminando todas las entidades y relaciones de Neo4j...")
    db.ejecutar_consulta(query)
    print(" Base de datos vaciada completamente.")


if __name__ == "__main__":
    # Confirmación opcional de seguridad
    confirmacion = input(
        "¿Estás seguro de que deseas eliminar TODOS los datos? (s/n): "
    )
    if confirmacion.lower() == "s":
        vaciar_base_datos()
    else:
        print("Operación cancelada.")