# RedPro — interfaz gráfica para I+D de Bases de Datos

Aplicación web en **Streamlit**, conectada a la misma base **Neo4j** del proyecto original. Conserva la lógica Python y añade módulos de usuarios, empresas, habilidades, proyectos, vacantes, conexiones, consultas, recomendaciones y mapa interactivo del grafo.

## Cómo ejecutarla en Windows (PowerShell)

1. Extrae el ZIP y abre la carpeta `Proyecto_I-D_BD-main` en VS Code.
2. Asegúrate de que Neo4j esté encendido y tengas su usuario, contraseña y dirección Bolt.
3. Desde la terminal de VS Code, dentro de la carpeta del proyecto, ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell impide activar el entorno, puedes ejecutar el resto con `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` y `.\.venv\Scripts\python.exe -m streamlit run app.py`.

4. Duplica `.env.example` con el nombre `.env` y pon los valores reales:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tu_clave_real
```

Si usas Neo4j Aura, copia la URI `neo4j+s://...` de Aura en lugar de la dirección local.

5. Si la base está vacía, primero ejecuta `python cargar_datos.py` (solo una vez, porque el script original puede crear registros repetidos). Si ya tiene datos, NO vuelvas a cargar datos.
6. Abre la aplicación:

```powershell
streamlit run app.py
```

Streamlit normalmente abre `http://localhost:8501` automáticamente.

## Orden recomendado para la demostración

1. **Inicio:** estadísticas del grafo y habilidades demandadas.
2. **Usuarios:** registro y edición de un profesional.
3. **Empresas / Empleos:** registrar una empresa y una vacante.
4. **Conexiones:** vincular profesional-habilidad y empresa-vacante; hacer una postulación.
5. **Explorador del grafo:** mostrar visualmente relaciones y nodos.
6. **Recomendaciones / Consultas:** obtener resultados reales de Neo4j.

## Archivos añadidos

- `app.py`: aplicación web.
- `servicios_gui.py`: consultas de lectura para poblar tablas, indicadores y el mapa.
- `.env.example`: ejemplo seguro de configuración.
- `requirements.txt`: dependencias mínimas del proyecto con Streamlit y PyVis.
- `requirements_original.txt`: requisitos que venían en la entrega original.

## Advertencias

- Esta interfaz no usa datos inventados ni base de datos simulada: **debe conectarse a Neo4j**.
- No existe una base Neo4j accesible desde este entorno para hacer una prueba de extremo a extremo: se ha verificado la sintaxis Python, no la conexión en vivo ni todas las consultas Cypher.
- El servidor es una herramienta académica local sin inicio de sesión propio; no lo expongas públicamente.
- El nombre de algunas relaciones del repositorio es distinto del enunciado (`POSEE` en vez de `TIENE_HABILIDAD`, `SE_POSTULA_A` en vez de `POSTULA_A`). La interfaz respeta los nombres **implementados realmente** en el código.
- Para un despliegue real hacen falta validaciones adicionales, control de acceso y pruebas de integración.
