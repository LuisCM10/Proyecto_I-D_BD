from entidades.usuario import Usuario

# Instanciar el repositorio
repo_usuario = Usuario()

# Crear el nodo para un usuario

'''nuevo_usuario = repo_usuario.crear(
    nombre="Luis Felipe Carrillo Molina",
    correo="carrillolf@uninorte.edu.co",
    telefono="+57 320 728 0384",
    ubicacion="Barranquilla, Colombia",
    experiencia="Estudiante de Ingeniería de Sistemas con experiencia en Backend (FastAPI, SQLAlchemy), Analítica de Grafos y Desarrollo Embebido/VHDL",
    educacion="Ingeniería de Sistemas - Universidad del Norte",
)

print("Usuario creado exitosamente:", nuevo_usuario)'''

# eliminar un usuario por su ID
'''usuario_id_a_eliminar = "usr_0"  # Reemplaza con el ID del usuario que deseas eliminar
resultado_eliminacion = repo_usuario.eliminar(usuario_id_a_eliminar)
print("Resultado de la eliminación:", resultado_eliminacion)'''

from entidades.controller import crear_restricciones_unicidad

crear_restricciones_unicidad()