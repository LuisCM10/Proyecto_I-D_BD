# Job to go — plataforma profesional con Neo4j

Proyecto académico de I+D de Bases de Datos. Aplicación en **Python + Streamlit**, con base de datos de grafos **Neo4j**, para profesionales, empresas y administradores.

## Instalar y ejecutar en Windows

1. Abre esta carpeta en VS Code.
2. Conserva tu archivo `.env` de la versión anterior. Si instalas desde cero, copia `.env.example` a `.env` y completa los valores privados de Neo4j y del administrador.
3. En la terminal, ejecuta:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Abre `http://localhost:8501`.

**Si ya tienes la base cargada, no ejecutes `cargar_datos.py`.** El modo de acceso por correo/nombre repetido como contraseña es **solo para una demostración local**; no debe desplegarse públicamente ni utilizarse con datos reales sensibles.

## Novedades de esta versión

- **Tema blanco y azul** para toda la aplicación, incluido el Dashboard, los formularios, las tarjetas, el menú lateral y el explorador gráfico.
- **Mi red** en el perfil profesional incluye:
  - **Descubrir personas:** enviar solicitudes de conexión.
  - **Recibidas:** aceptar o rechazar solicitudes.
  - **Enviadas:** consultar y cancelar solicitudes pendientes.
  - **Mis conexiones:** ver profesionales conectados.
- El menú indica cuántas invitaciones hay pendientes de respuesta.
- El Explorador del grafo muestra las solicitudes pendientes con **líneas discontinuas**.
- Se conserva la gestión de perfiles, habilidades, vacantes, proyectos, postulaciones, recomendaciones y consultas existentes.

### Modelo de las solicitudes

No se crea ninguna nueva entidad (nodo). Se añade únicamente un **tipo de relación**:

- `(Usuario)-[:SOLICITA_CONEXION]->(Usuario)` al enviar una invitación.
- Al **aceptar**, la aplicación elimina esa solicitud y crea la relación existente `CONECTA_CON`.
- Al **rechazar** o **cancelar**, elimina la solicitud sin crear una conexión.

De ese modo, las recomendaciones basadas en `CONECTA_CON` no confunden solicitudes con amistades confirmadas. Los registros de usuarios anteriores y sus relaciones `CONECTA_CON` siguen siendo válidos.

## Prueba recomendada de la función social

1. Inicia sesión como **Profesional A**.
2. En **Mi red → Descubrir personas**, elige a un profesional **que todavía no esté conectado** contigo y pulsa **Conectar**.
3. Comprueba la pestaña **Enviadas**.
4. Cierra sesión y entra con el perfil del **Profesional B**.
5. Ve a **Mi red → Recibidas** y pulsa **Aceptar** o **Rechazar**.
6. Si aceptas, la persona pasará a **Mis conexiones** en ambos perfiles; si rechazas, podrá volver a recibir una solicitud.

Estas operaciones **escriben en Neo4j**. Si la base pertenece al grupo, coordina las pruebas antes de modificarla.


## Vinculación laboral y participación en proyectos

**Sin crear nodos nuevos.** Se reutilizan las relaciones existentes de Neo4j:

- `(:Usuario)-[:TRABAJA_EN]->(:Empresa)` permite que el profesional vea la empresa donde trabaja en **Inicio** y **Mi perfil**. La empresa ve estos profesionales en **Mi empresa → Empleados vinculados**.
- `(:Empresa)-[:TIENE]->(:Proyecto)` determina qué proyectos puede solicitar un empleado. El profesional los ve en **Proyectos de mi empresa**, en su menú.
- `(:Usuario)-[:SOLICITA_PARTICIPACION]->(:Proyecto)` representa una solicitud *pendiente*. No cuenta como participación confirmada.
- Tras pulsar **Aceptar** desde **Empresa → Mis proyectos**, la solicitud se elimina y se crea `(:Usuario)-[:PARTICIPA_EN]->(:Proyecto)`. **Rechazar** elimina solo la solicitud. El profesional puede **Cancelar** una solicitud enviada.

Una empresa **solo puede aprobar solicitudes de sus proyectos** y de personas que aún están vinculadas a ella mediante `TRABAJA_EN`. Si un empleado no ve su empresa, revisa la relación existente: el administrador puede crearla en **Conexiones → Vincular profesional a empresa**. No se crean relaciones laborales automáticamente.

### Prueba rápida

1. Con el administrador, comprueba una relación `TRABAJA_EN` y un proyecto asociado a esa empresa mediante `TIENE`.
2. Entra como el profesional y consulta **Mi perfil → Mi empresa** y **Proyectos de mi empresa**.
3. Pulsa **Solicitar ingreso** y comprueba el estado **Pendiente**.
4. Entra con la empresa propietaria y abre **Mis proyectos → Solicitudes de participación**.
5. Pulsa **Aceptar** (o **Rechazar**) y comprueba desde el perfil profesional el resultado.

**Advertencia:** estas acciones escriben relaciones en Neo4j. En una base compartida, realiza las pruebas con permiso. El acceso de demostración por correo/nombre repetido no constituye una autenticación segura y no es apto para producción.

## Archivos importantes

- `app.py`: interfaz, navegación, roles, pestañas sociales y tema CSS.
- `jobtogo_operaciones.py`: lógica de Neo4j para perfiles, empresas, vacantes, habilidades, proyectos y solicitudes.
- `.streamlit/config.toml`: tema claro de Streamlit.
- `conexion.py`: conexión compartida con Neo4j.
- `servicios_gui.py`: consultas para paneles y tablas.
- `.env.example`: plantilla sin contraseñas reales.

## Consideraciones

- **No se incluyen credenciales** `.env` ni `.env.backup` en esta entrega.
- La lógica de conexiones se verificó localmente con llamadas simuladas y pruebas de sintaxis. La interacción real con tu instancia de Neo4j requiere probarse desde tu computador.
- Este inicio de sesión académico no autentica identidades de forma segura. Antes de publicar el sitio en internet hay que implementar autenticación y control de permisos robustos.

---

## Actualización: ciclo completo de empleo y notificaciones (noviembre 2026)

La versión actual incorpora los siguientes módulos adicionales, conservando **Job to go** y el tema blanco/azul:

| Perfil | Sección | Funcionalidad |
| --- | --- | --- |
| Profesional | Buscar empleos | Búsqueda por texto, ubicación, empresa, contrato, habilidades, salario y compatibilidad |
| Profesional | Empleos guardados | Guardar y quitar vacantes favoritas (`GUARDA_OFERTA`) |
| Profesional | Mis postulaciones | Ver estado: Pendiente / En revisión / Aceptada / Rechazada |
| Profesional | Mi empresa laboral | Pedir ingreso a una empresa y solicitar desvinculación |
| Profesional | Mi perfil | Indicador de campos completados |
| Profesional y empresa | Notificaciones | Avisos internos derivados del grafo, con contador de elementos sin leer |
| Empresa | Solicitudes laborales | Aceptar o rechazar solicitudes de ingreso o desvinculación |
| Empresa | Candidatos | Actualizar el estado de las postulaciones recibidas para sus propias vacantes |
| Empresa | Mis vacantes | Cerrar o reabrir vacantes y actualizar su fecha de cierre |

No se crean tipos de **nodos** nuevos. Se agregan relaciones `GUARDA_OFERTA`, `SOLICITA_VINCULACION`, `SOLICITA_DESVINCULACION` y propiedades `estado`/fechas en relaciones y ofertas existentes. `notificaciones_vistas` es una lista guardada como propiedad del nodo Usuario/Empresa. Por tanto, para usar estas funciones debes tener permisos de **escritura** en Neo4j.

### Importante: ofertas vencidas

Las vacantes cuya `fecha_cierre` sea anterior al día actual se muestran como **Vencidas** y no aceptan postulaciones nuevas. Muchas ofertas del dataset académico original tienen fechas de cierre en marzo y abril de 2026. Para probar una postulación hoy, la empresa propietaria debe ir a **Mis vacantes → Cerrar o reabrir vacantes**, seleccionar una fecha futura y pulsar **Reabrir vacante**. **No vuelvas a ejecutar `cargar_datos.py`** para esto.

### Instalación por actualización sobre el proyecto que ya funciona

1. Guarda copia de `app.py`, `jobtogo_operaciones.py` y `consultas/StmRecomendacion.py`.
2. Copia los archivos proporcionados por la actualización dentro de la carpeta raíz del proyecto, respetando el subdirectorio `consultas/`.
3. **No cambies tu `.env` ni ejecutes `cargar_datos.py`.**
4. Corre:

   ```powershell
   python -m streamlit run app.py
   ```

Si te faltan dependencias: `python -m pip install -r requirements.txt`.

### Pruebas recomendadas para la presentación

- **Empleo:** entra como profesional y filtra empleos; guarda uno y revisa `Empleos guardados`.
- **Postulación:** selecciona una oferta abierta, pulsa `Postularme`; entra como la empresa propietaria y cambia su estado en `Candidatos`. Vuelve al usuario y verifica `Mis postulaciones` y `Notificaciones`.
- **Vinculación:** en `Mi empresa laboral`, solicita unirte a una empresa. Inicia sesión como esa empresa, aprueba en `Solicitudes laborales` y confirma que aparece en `Mi empresa` como empleado.
- **Vacantes:** cierra y reabre una vacante desde `Mis vacantes`; verifica que una cerrada no acepte nuevas postulaciones.
- **Perfil:** visualiza el indicador de completitud en `Mi perfil` y complétalo con tus habilidades.
- **Notificaciones:** entra a cada perfil, marca sus avisos como leídos y comprueba el contador.

### Pruebas de código sin Neo4j

Ejecuta `python test_mejoras_local.py` para verificar reglas de validación, consultas parametrizadas, caducidad, propiedad de candidaturas y duplicados mediante simulaciones. Estas pruebas **no sustituyen** una prueba de flujo real conectada a Neo4j.

### Límites de esta entrega

Las notificaciones son internas (no envían correo ni mensajes push); algunas respuestas históricas que borran solicitudes, como rechazos de conexiones o proyectos, no permanecen en el centro de avisos. Los mensajes sin leer se marcan persistiendo claves en el perfil.

El inicio de sesión sigue siendo el de **demostración local**, con el correo o nombre de empresa repetido como clave. **No es seguro**: cualquier persona que conozca esos datos podría realizar operaciones en nombre de otra. **No publiques esta aplicación ni la expongas a redes externas con acceso de escritura** hasta implementar autenticación real y autorización verificable en el servidor.
