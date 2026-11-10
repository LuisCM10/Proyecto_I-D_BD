# cargar_datos.py

from conexion import db
from datos.datos_estructurados import (
    EMPRESAS, HABILIDADES, TECNOLOGIAS, PROYECTOS, OFERTAS_LABORALES, USUARIOS,
    RELACIONES_EMPRESA_OFERTA, RELACIONES_EMPRESA_PROYECTO, RELACIONES_PROYECTO_TECNOLOGIA,
    RELACIONES_OFERTA_HABILIDAD, RELACIONES_USUARIO_USUARIO, RELACIONES_USUARIO_EMPRESA,
    RELACIONES_USUARIO_HABILIDAD, RELACIONES_USUARIO_PROYECTO, RELACIONES_USUARIO_OFERTA
)
from entidades.controller import crear_restricciones_unicidad
from entidades.empresa import Empresa
from entidades.habilidad import Habilidad
from entidades.tecnologia import Tecnologia
from entidades.proyecto import Proyecto
from entidades.oferta_laboral import OfertaLaboral
from entidades.usuario import Usuario

def poblar_base_datos_completa():
    print("--- 🗑️ 1. Limpiando base de datos ---")
    db.ejecutar_consulta("MATCH (n) DETACH DELETE n")
    print(" Base de datos vaciada.\n")

    print("--- 🔒 2. Aplicando restricciones de unicidad ---")
    crear_restricciones_unicidad()
    print()

    empresa_model = Empresa()
    habilidad_model = Habilidad()
    tecnologia_model = Tecnologia()
    proyecto_model = Proyecto()
    oferta_model = OfertaLaboral()
    usuario_model = Usuario()

    map_empresas = []
    map_habilidades = []
    map_tecnologias = []
    map_proyectos = []
    map_ofertas = []
    map_usuarios = []

    print("--- 📦 3. Creando 5+ Nodos por Entidad ---")

    for emp in EMPRESAS:
        res = empresa_model.crear(**emp)
        e_id = res[0]["e"]["id"]
        map_empresas.append(e_id)
        print(f"✓ Empresa ({e_id}): {emp['nombre']}")

    for hab in HABILIDADES:
        res = habilidad_model.crear(**hab)
        h_id = res[0]["h"]["id"]
        map_habilidades.append(h_id)
        print(f"✓ Habilidad ({h_id}): {hab['nombre']}")

    for tec in TECNOLOGIAS:
        res = tecnologia_model.crear(**tec)
        t_id = res[0]["t"]["id"]
        map_tecnologias.append(t_id)
        print(f"✓ Tecnología ({t_id}): {tec['nombre']}")

    for proy in PROYECTOS:
        res = proyecto_model.crear(**proy)
        p_id = res[0]["p"]["id"]
        map_proyectos.append(p_id)
        print(f"✓ Proyecto ({p_id}): {proy['nombre']}")

    for ofe in OFERTAS_LABORALES:
        res = oferta_model.crear(**ofe)
        o_id = res[0]["o"]["id"]
        map_ofertas.append(o_id)
        print(f"✓ Oferta ({o_id}): {ofe['titulo']}")

    for usr in USUARIOS:
        res = usuario_model.crear(**usr)
        u_id = res[0]["u"]["id"]
        map_usuarios.append(u_id)
        print(f"✓ Usuario ({u_id}): {usr['nombre']}")

    print("\n--- 🔗 4. Conectando Relaciones del Grafo ---")

    for idx_emp, idx_ofe in RELACIONES_EMPRESA_OFERTA:
        empresa_model.publica_oferta(map_empresas[idx_emp], map_ofertas[idx_ofe])

    for idx_emp, idx_proy in RELACIONES_EMPRESA_PROYECTO:
        empresa_model.tiene_proyecto(map_empresas[idx_emp], map_proyectos[idx_proy])

    for idx_proy, idx_tec in RELACIONES_PROYECTO_TECNOLOGIA:
        proyecto_model.usa_tecnologia(map_proyectos[idx_proy], map_tecnologias[idx_tec])

    for idx_ofe, idx_hab in RELACIONES_OFERTA_HABILIDAD:
        oferta_model.requiere_tener(map_ofertas[idx_ofe], map_habilidades[idx_hab])

    for idx_u1, idx_u2 in RELACIONES_USUARIO_USUARIO:
        usuario_model.conecta_con(map_usuarios[idx_u1], map_usuarios[idx_u2])

    for idx_u, idx_emp in RELACIONES_USUARIO_EMPRESA:
        usuario_model.trabaja_en(map_usuarios[idx_u], map_empresas[idx_emp])

    for idx_u, idx_hab in RELACIONES_USUARIO_HABILIDAD:
        usuario_model.posee_habilidad(map_usuarios[idx_u], map_habilidades[idx_hab])

    for idx_u, idx_proy in RELACIONES_USUARIO_PROYECTO:
        usuario_model.participa_en(map_usuarios[idx_u], map_proyectos[idx_proy])

    for idx_u, idx_ofe in RELACIONES_USUARIO_OFERTA:
        usuario_model.se_postula_a(map_usuarios[idx_u], map_ofertas[idx_ofe])

    print("\n ¡Poblado completado con éxito! Todas las entidades poseen al menos 5 nodos.")

if __name__ == "__main__":
    poblar_base_datos_completa()