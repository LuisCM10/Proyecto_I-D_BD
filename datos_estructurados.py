# datos_ficticios.py

EMPRESAS = [
    {
        "nombre": "TechSolutions Colombia",
        "industria": "Desarrollo de Software",
        "ubicacion": "Bogotá, Colombia",
        "tamano": "Grande (250+ empleados)",
        "descripcion": "Especializados en arquitectura cloud y microservicios escalables."
    },
    {
        "nombre": "Caribe Analytics",
        "industria": "Consultoría de Datos",
        "ubicacion": "Barranquilla, Colombia",
        "tamano": "Mediana (50-200 empleados)",
        "descripcion": "Firma enfocada en ciencia de datos, bases de datos de grafos y BI."
    },
    {
        "nombre": "CloudSec Latam",
        "industria": "Ciberseguridad",
        "ubicacion": "Medellín, Colombia",
        "tamano": "Mediana (100-250 empleados)",
        "descripcion": "Soluciones de seguridad ofensiva, hardening e infraestructura segura."
    },
    {
        "nombre": "Banquia Digital",
        "industria": "Fintech & Banca Digital",
        "ubicacion": "Bogotá, Colombia",
        "tamano": "Grande (500+ empleados)",
        "descripcion": "Neobanco enfocado en microfinanzas y procesamiento de transacciones masivas."
    },
    {
        "nombre": "IoT Caribe Systems",
        "industria": "Sistemas Embebidos e IoT",
        "ubicacion": "Barranquilla, Colombia",
        "tamano": "Startup (20-50 empleados)",
        "descripcion": "Desarrollo de hardware y telemetría industrial en tiempo real con FPGAs y micros."
    }
]

HABILIDADES = [
    {"nombre": "Python", "categoria": "Programación", "nivel": "Avanzado"},
    {"nombre": "Neo4j / Cypher", "categoria": "Bases de Datos de Grafos", "nivel": "Avanzado"},
    {"nombre": "FastAPI", "categoria": "Desarrollo Backend", "nivel": "Intermedio"},
    {"nombre": "Docker / Containerization", "categoria": "DevOps", "nivel": "Avanzado"},
    {"nombre": "Wireshark / Network Security", "categoria": "Ciberseguridad", "nivel": "Intermedio"},
    {"nombre": "NumPy & Pandas", "categoria": "Ciencia de Datos", "nivel": "Avanzado"}
]

TECNOLOGIAS = [
    {"nombre": "Python", "categoria": "Lenguaje", "descripcion": "Lenguaje multipropósito para backend y datos."},
    {"nombre": "Neo4j", "categoria": "Base de Datos", "descripcion": "Motor de base de datos orientada a grafos."},
    {"nombre": "Docker", "categoria": "DevOps", "descripcion": "Plataforma de contenerización."},
    {"nombre": "FastAPI", "categoria": "Framework", "descripcion": "Framework asíncrono para creación de APIs en Python."},
    {"nombre": "Pandas", "categoria": "Ciencia de Datos", "descripcion": "Librería para análisis y manipulación de datos."},
    {"nombre": "Wireshark", "categoria": "Seguridad", "descripcion": "Herramienta de análisis de protocolos de red."}
]

PROYECTOS = [
    {
        "nombre": "Motor de Recomendaciones Laborales en Grafos",
        "descripcion": "Sistema de recomendación de empleos y contactos sobre Neo4j.",
        "fecha_inicio": "2026-01-15",
        "fecha_fin": "2026-06-30"
    },
    {
        "nombre": "Auditoría de Microservicios Backend",
        "descripcion": "Escaneo de vulnerabilidades y hardening de contenedores en FastAPI.",
        "fecha_inicio": "2026-02-10",
        "fecha_fin": "2026-07-20"
    },
    {
        "nombre": "Pipeline ETL para Métricas de Productividad",
        "descripcion": "Procesamiento de datos de productividad de desarrolladores con Pandas.",
        "fecha_inicio": "2026-04-01",
        "fecha_fin": "2026-06-15"
    },
    {
        "nombre": "Plataforma de Analítica Financiera",
        "descripcion": "Dashboard interactivo para transacciones y detección de fraudes.",
        "fecha_inicio": "2026-01-10",
        "fecha_fin": "2026-08-15"
    },
    {
        "nombre": "Monitoreo Embebido de Calidad de Aire CO2",
        "descripcion": "Sistema embebido en Nios II / FPGA para telemetría ambiental.",
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2026-11-30"
    }
]

OFERTAS_LABORALES = [
    {
        "titulo": "Senior Graph Database Developer",
        "descripcion": "Especialista en Neo4j y Cypher para consultas de recomendación de alta concurrencia.",
        "fecha_publicacion": "2026-03-01",
        "fecha_cierre": "2026-04-15",
        "ubicacion": "Barranquilla (Híbrido)",
        "salario": 7500000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "DevOps & Cloud Security Engineer",
        "descripcion": "Especialista en infraestructura cloud, Docker y auditorías de seguridad en red.",
        "fecha_publicacion": "2026-03-10",
        "fecha_cierre": "2026-04-30",
        "ubicacion": "Bogotá (Remoto)",
        "salario": 8200000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "Ingeniero de Datos & Econometría",
        "descripcion": "Modelado predictivo y manipulación de grandes volúmenes de datos con Pandas.",
        "fecha_publicacion": "2026-03-12",
        "fecha_cierre": "2026-04-25",
        "ubicacion": "Medellín (Híbrido)",
        "salario": 6800000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "Backend FastAPI Developer",
        "descripcion": "Desarrollador de microservicios REST/GraphQL asíncronos en Python.",
        "fecha_publicacion": "2026-03-05",
        "fecha_cierre": "2026-04-20",
        "ubicacion": "Bogotá (Híbrido)",
        "salario": 6500000.0,
        "tipo_contrato": "Término Indefinido"
    },
    {
        "titulo": "Embedded Systems Developer",
        "descripcion": "Desarrollador de firmware y hardware para control industrial con C, VHDL y ensamblador.",
        "fecha_publicacion": "2026-03-01",
        "fecha_cierre": "2026-04-15",
        "ubicacion": "Barranquilla (Presencial)",
        "salario": 5500000.0,
        "tipo_contrato": "Término Indefinido"
    }
]

USUARIOS = [
    {
        "nombre": "Luis Felipe Carrillo Molina",
        "correo": "luiscarrillo@uninorte.edu.co",
        "telefono": "+57 300 123 4567",
        "ubicacion": "Barranquilla, Colombia",
        "experiencia": "Desarrollo backend, diseño de grafos en Neo4j y arquitectura de software.",
        "educacion": "Ingeniería de Sistemas - Universidad del Norte"
    },
    {
        "nombre": "María Alejandra Torres",
        "correo": "maria.torres@techcorp.com",
        "telefono": "+57 315 987 6543",
        "ubicacion": "Bogotá, Colombia",
        "experiencia": "Líder de ingeniería de datos y desarrollo backend en Python.",
        "educacion": "Ingeniería de Sistemas - Universidad Nacional"
    },
    {
        "nombre": "Carlos Eduardo Gómez",
        "correo": "carlos.gomez@analytics.io",
        "telefono": "+57 301 456 7890",
        "ubicacion": "Medellín, Colombia",
        "experiencia": "Analítica de datos, modelos predictivos y consultas optimizadas Cypher.",
        "educacion": "Ciencia de Datos - Universidad de Antioquia"
    },
    {
        "nombre": "Daniela Sofía Mendoza",
        "correo": "daniela.mendoza@cloudsec.co",
        "telefono": "+57 311 888 9900",
        "ubicacion": "Bogotá, Colombia",
        "experiencia": "Ciberseguridad, análisis de tráfico con Wireshark y contenedores Docker.",
        "educacion": "Ingeniería de Sistemas - Universidad de los Andes"
    },
    {
        "nombre": "Andrea Sofía López",
        "correo": "andrea.lopez@innosoft.co",
        "telefono": "+57 302 555 4433",
        "ubicacion": "Barranquilla, Colombia",
        "experiencia": "Desarrollo embebido, microcontroladores y programación en VHDL/Ensamblador.",
        "educacion": "Ingeniería Electrónica - Universidad del Norte"
    }
]

# Matriz de relaciones (basada en índices de listas 0-4)
RELACIONES_EMPRESA_OFERTA = [(1, 0), (2, 1), (3, 2), (0, 3), (4, 4)]
RELACIONES_EMPRESA_PROYECTO = [(1, 0), (2, 1), (3, 2), (0, 3), (4, 4)]

RELACIONES_PROYECTO_TECNOLOGIA = [
    (0, 0), (0, 1), (0, 3),  # Proyecto 0 (Grafos) usa Python, Neo4j, FastAPI
    (1, 2), (1, 3), (1, 5),  # Proyecto 1 (Microservicios) usa Docker, FastAPI, Wireshark
    (2, 0), (2, 4),          # Proyecto 2 (ETL) usa Python, Pandas
    (3, 0), (3, 3),          # Proyecto 3 (Financiera) usa Python, FastAPI
    (4, 0)                   # Proyecto 4 (CO2) usa Python
]

RELACIONES_OFERTA_HABILIDAD = [
    (0, 0), (0, 1),  # Oferta 0 requiere Python, Neo4j
    (1, 3), (1, 4),  # Oferta 1 requiere Docker, Wireshark
    (2, 0), (2, 5),  # Oferta 2 requiere Python, NumPy & Pandas
    (3, 0), (3, 2),  # Oferta 3 requiere Python, FastAPI
    (4, 0)           # Oferta 4 requiere Python
]

RELACIONES_USUARIO_USUARIO = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (4, 0)]
RELACIONES_USUARIO_EMPRESA = [(0, 1), (1, 0), (2, 1), (3, 2), (4, 4)]

RELACIONES_USUARIO_HABILIDAD = [
    (0, 0), (0, 1), (0, 2),  # Luis (Python, Neo4j, FastAPI)
    (1, 0), (1, 2), (1, 3),  # María (Python, FastAPI, Docker)
    (2, 0), (2, 1), (2, 5),  # Carlos (Python, Neo4j, Pandas)
    (3, 3), (3, 4),          # Daniela (Docker, Wireshark)
    (4, 0), (4, 2)           # Andrea (Python, FastAPI)
]

RELACIONES_USUARIO_PROYECTO = [(0, 0), (0, 4), (1, 3), (2, 0), (3, 1), (4, 4)]
RELACIONES_USUARIO_OFERTA = [(0, 0), (2, 0), (3, 1), (4, 4)]