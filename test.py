from entidades.usuario import Usuario

# Instanciar el repositorio
repo_usuario = Usuario()

# Crear o actualizar el nodo para un usuario
nuevo_usuario = repo_usuario.crear(
    usuario_id="usr_0",
    nombre="Luis Felipe Carrillo Molina",
    correo="carrillolf@uninorte.edu.co",
    telefono="+57 320 728 0384",
    ubicacion="Barranquilla, Colombia",
    experiencia="Estudiante de Ingeniería de Sistemas con experiencia en Backend (FastAPI, SQLAlchemy), Analítica de Grafos y Desarrollo Embebido/VHDL",
    educacion="Ingeniería de Sistemas - Universidad del Norte",
)

print("Usuario creado/actualizado exitosamente:", nuevo_usuario)