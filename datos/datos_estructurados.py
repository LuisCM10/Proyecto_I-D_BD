
EMPRESAS = [
    {
        "nombre": "TechSolutions Colombia",
        "industria": "Desarrollo de Software",
        "ubicacion": "Bogotá, Colombia",
        "tamano": "Grande (250+ empleados)",
        "descripcion": "Empresa especializada en soluciones cloud y analítica de datos a gran escala."
    },
    {
        "nombre": "Caribe Analytics",
        "industria": "Consultoría de Datos",
        "ubicacion": "Barranquilla, Colombia",
        "tamano": "Mediana (50-200 empleados)",
        "descripcion": "Firma enfocada en inteligencia de negocios, grafos y ciencia de datos."
    },
    {
        "nombre": "InnoSoft Latam",
        "industria": "Ciberseguridad y Backend",
        "ubicacion": "Medellín, Colombia",
        "tamano": "Startup (15-50 empleados)",
        "descripcion": "Desarrollamos infraestructura backend segura para fintechs."
    }
]

HABILIDADES = [
    {"nombre": "Python", "categoria": "Programación", "nivel": "Avanzado"},
    {"nombre": "Neo4j / Cypher", "categoria": "Bases de Datos de Grafos", "nivel": "Avanzado"},
    {"nombre": "FastAPI", "categoria": "Desarrollo Backend", "nivel": "Intermedio"},
    {"nombre": "PostgreSQL", "categoria": "Bases de Datos Relacionales", "nivel": "Avanzado"},
    {"nombre": "VHDL / FPGA", "categoria": "Sistemas Embebidos", "nivel": "Intermedio"},
    {"nombre": "Machine Learning", "categoria": "Ciencia de Datos", "nivel": "Intermedio"}
]

PROYECTOS = [
    {
        "nombre": "Motor de Recomendaciones Laborales en Grafos",
        "descripcion": "Sistema de recomendación basado en centralidad y coincidencia de habilidades sobre Neo4j.",
        "fecha_inicio": "2026-01-15",
        "fecha_fin": "2026-06-30",
        "tecnologias": "Python, Neo4j, Cypher, FastAPI"
    },
    {
        "nombre": "Monitoreo Embebido de Calidad de Aire CO2",
        "descripcion": "Sistema de monitoreo en tiempo real implementado en procesadores Nios II / FPGA.",
        "fecha_inicio": "2026-02-01",
        "fecha_fin": "2026-05-15",
        "tecnologias": "Nios II Assembly, VHDL, C"
    },
    {
        "nombre": "Plataforma de Analítica Financiera",
        "descripcion": "API REST para consolidación de ingresos, gastos y predicción de flujo de caja.",
        "fecha_inicio": "2025-08-10",
        "fecha_fin": "2025-12-20",
        "tecnologias": "Python, PostgreSQL, SQLAlchemy"
    }
]

OFERTAS_LABORALES = [
    {
        "titulo": "Senior Graph Database Developer",
        "descripcion": "Buscamos un especialista en Neo4j y Cypher para optimización de consultas de recomendación.",
        "fecha_publicacion": "2026-03-01",
        "fecha_cierre": "2026-04-15",
        "ubicacion": "Barranquilla (Híbrido)",
        "salario": 7500000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "Desarrollador Backend Python / FastAPI",
        "descripcion": "Construcción de microservicios escalables y procesamiento de datos asíncrono.",
        "fecha_publicacion": "2026-03-05",
        "fecha_cierre": "2026-04-30",
        "ubicacion": "Bogotá (Remoto)",
        "salario": 6000000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "Consultor Junior en Ciencia de Datos",
        "descripcion": "Apoyo en modelos de machine learning y estructuración de pipelines de datos.",
        "fecha_publicacion": "2026-02-20",
        "fecha_cierre": "2026-03-31",
        "ubicacion": "Medellín (Presencial)",
        "salario": 3800000.0,
        "tipo_contrato": "Prestación de Servicios"
    }
]

USUARIOS = [
    {
        "nombre": "Luis Felipe Carrillo Molina",
        "correo": "carrillolf@uninorte.edu.co",
        "telefono": "+57 300 123 4567",
        "ubicacion": "Barranquilla, Colombia",
        "experiencia": "3 años en desarrollo backend, diseño de grafos en Neo4j y arquitectura embebida.",
        "educacion": "Ingeniería de Sistemas - Universidad del Norte"
    },
    {
        "nombre": "María Alejandra Torres",
        "correo": "maria.torres@techcorp.com",
        "telefono": "+57 315 987 6543",
        "ubicacion": "Bogotá, Colombia",
        "experiencia": "5 años liderando equipos de ingeniería de datos y desarrollo backend en Python.",
        "educacion": "Ingeniería de Sistemas - Universidad Nacional"
    },
    {
        "nombre": "Carlos Eduardo Gómez",
        "correo": "carlos.gomez@analytics.io",
        "telefono": "+57 301 456 7890",
        "ubicacion": "Medellín, Colombia",
        "experiencia": "2 años en analítica de datos, modelos predictivos y consultas Cypher.",
        "educacion": "Ciencia de Datos - Universidad de Antioquia"
    },
    {
        "nombre": "Andrea Sofía López",
        "correo": "andrea.lopez@innosoft.co",
        "telefono": "+57 320 654 3210",
        "ubicacion": "Barranquilla, Colombia",
        "experiencia": "4 años en frontend interactivo y consumo de APIs GraphQL/REST.",
        "educacion": "Ingeniería Industrial - Universidad del Norte"
    }
]

# Definición de relaciones entre índices de las listas superiores
# (Formatos indexados a 0 para automatización de carga)

RELACIONES_EMPRESA_OFERTA = [
    (0, 1),  # TechSolutions PUBLICA Oferta "Desarrollador Backend Python"
    (1, 0),  # Caribe Analytics PUBLICA Oferta "Senior Graph Database Developer"
    (2, 2)   # InnoSoft Latam PUBLICA Oferta "Consultor Junior en Ciencia de Datos"
]

RELACIONES_EMPRESA_PROYECTO = [
    (1, 0),  # Caribe Analytics TIENE Proyecto "Motor de Recomendaciones Laborales"
    (2, 1),  # InnoSoft Latam TIENE Proyecto "Monitoreo Embebido de Calidad de Aire CO2"
    (0, 2)   # TechSolutions TIENE Proyecto "Plataforma de Analítica Financiera"
]

RELACIONES_OFERTA_HABILIDAD = [
    (0, 0),  # Senior Graph Dev REQUIERE Python
    (0, 1),  # Senior Graph Dev REQUIERE Neo4j / Cypher
    (1, 0),  # Backend Dev REQUIERE Python
    (1, 2),  # Backend Dev REQUIERE FastAPI
    (1, 3),  # Backend Dev REQUIERE PostgreSQL
    (2, 0),  # Consultor Junior REQUIERE Python
    (2, 5)   # Consultor Junior REQUIERE Machine Learning
]

RELACIONES_USUARIO_USUARIO = [
    (0, 1),  # Luis CONECTA_CON María
    (0, 2),  # Luis CONECTA_CON Carlos
    (1, 2),  # María CONECTA_CON Carlos
    (2, 3)   # Carlos CONECTA_CON Andrea
]

RELACIONES_USUARIO_EMPRESA = [
    (0, 1),  # Luis TRABAJA_EN Caribe Analytics
    (1, 0),  # María TRABAJA_EN TechSolutions
    (2, 2)   # Carlos TRABAJA_EN InnoSoft Latam
]

RELACIONES_USUARIO_HABILIDAD = [
    (0, 0),  # Luis TIENE Python
    (0, 1),  # Luis TIENE Neo4j / Cypher
    (0, 2),  # Luis TIENE FastAPI
    (0, 4),  # Luis TIENE VHDL / FPGA
    (1, 0),  # María TIENE Python
    (1, 2),  # María TIENE FastAPI
    (1, 3),  # María TIENE PostgreSQL
    (2, 0),  # Carlos TIENE Python
    (2, 1),  # Carlos TIENE Neo4j / Cypher
    (2, 5)   # Carlos TIENE Machine Learning
]

RELACIONES_USUARIO_PROYECTO = [
    (0, 0),  # Luis PARTICIPA_EN Motor de Recomendaciones Laborales
    (0, 1),  # Luis PARTICIPA_EN Monitoreo Embebido
    (1, 2),  # María PARTICIPA_EN Plataforma de Analítica Financiera
    (2, 0)   # Carlos PARTICIPA_EN Motor de Recomendaciones Laborales
]

RELACIONES_USUARIO_OFERTA = [
    (0, 0),  # Luis SE_POSTULA_A Senior Graph Database Developer
    (2, 0),  # Carlos SE_POSTULA_A Senior Graph Database Developer
    (3, 2)   # Andrea SE_POSTULA_A Consultor Junior en Ciencia de Datos
]