# Job to go — Plataforma Profesional con Neo4j

Este es el repositorio de nuestro proyecto académico de I+D enfocado en Bases de Datos. Desarrollamos una aplicación web utilizando **Python y Streamlit** que se conecta a una base de datos de grafos en **Neo4j**. El objetivo de la plataforma es conectar a profesionales, empresas y administradores en un ecosistema laboral dinámico.

## Cómo arrancar el proyecto en Windows

Para probar la plataforma en tu máquina, sigue estos pasos:

* Abre la carpeta del proyecto en VS Code.
* Configura tus credenciales: si vienes de una versión anterior y ya tienes tu archivo `.env`, déjalo tal cual. Si es tu primera vez instalándolo, haz una copia del archivo `.env.example`, renómbrala a `.env` y completa ahí los datos de conexión a Neo4j y las credenciales del administrador.
* Abre la terminal y ejecuta lo siguiente para instalar las dependencias y levantar la interfaz:
  ```powershell
  python -m pip install -r requirements.txt
  python -m streamlit run app.py
  ```
* Entra a `http://localhost:8501` desde tu navegador.


## ¿Qué hay de nuevo en esta versión?

Le dimos una lavada de cara a la interfaz con un nuevo **tema blanco y azul** que se aplica a toda la app, incluyendo el dashboard, las tarjetas, los formularios y el explorador gráfico. Además, sumamos el ciclo completo de empleo y varias funciones sociales:

* **Módulo "Mi red":** Los profesionales ahora pueden descubrir a otras personas, enviarles solicitudes de conexión, aceptar o rechazar las recibidas, y cancelar las que dejaron pendientes. 
* **Indicadores visuales:** El menú lateral te avisa cuántas invitaciones tienes sin responder, y si abres el Explorador del grafo, verás las solicitudes pendientes marcadas con líneas discontinuas.
* **Búsqueda de empleo:** Ahora se pueden filtrar las vacantes por texto, ubicación, habilidades, tipo de contrato, salario y nivel de compatibilidad. 
* **Gestión de postulaciones:** Los profesionales pueden guardar sus empleos favoritos y hacerle seguimiento a sus postulaciones (para ver si están pendientes, en revisión, aceptadas o rechazadas). 
* **Opciones para empresas:** Las empresas pueden revisar a sus candidatos, aceptar o rechazar a profesionales que piden vincularse o desvincularse de la compañía, y administrar la apertura o cierre de sus vacantes.
* **Proyectos corporativos:** Los empleados pueden ver los proyectos de la empresa en la que trabajan y pedir participar en ellos. La empresa es la única que puede aprobar estas solicitudes.
* **Sistema de notificaciones:** Agregamos alertas internas para avisar a los usuarios sobre eventos del grafo, incluyendo un contador de mensajes no leídos.
* **Progreso del perfil:** El perfil del profesional ahora muestra un indicador de qué tan completos están sus datos.

## Así lo modelamos en Neo4j

Para mantener la base de datos limpia, decidimos **no crear nodos nuevos**, sino sacarle provecho a los tipos de relaciones y sus propiedades. 

* **Conexiones sociales:** Cuando alguien envía una invitación, creamos la relación `SOLICITA_CONEXION`. Si la otra persona acepta, borramos esa solicitud y creamos la relación `CONECTA_CON`. Si la rechaza, simplemente borramos la solicitud. Hicimos esto para que el algoritmo de recomendaciones no se confunda mezclando amigos reales con solicitudes en el aire.
* **Vínculos laborales:** Reutilizamos las relaciones `TRABAJA_EN` (del usuario a la empresa) y `TIENE` (de la empresa al proyecto). Si alguien quiere unirse a un proyecto, se crea `SOLICITA_PARTICIPACION`, que pasa a ser `PARTICIPA_EN` únicamente si la empresa lo aprueba.
* **Empleo y estados:** Implementamos relaciones como `GUARDA_OFERTA`, `SOLICITA_VINCULACION` y `SOLICITA_DESVINCULACION`. Las notificaciones se gestionan guardando una lista dentro de la propiedad `notificaciones_vistas` directamente en el nodo del usuario o de la empresa.