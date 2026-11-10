
from entidades.usuario import Usuario
from entidades.empresa import Empresa
from entidades.habilidad import Habilidad
from entidades.proyecto import Proyecto
from entidades.oferta_laboral import OfertaLaboral

from datos.datos_estructurados import (
    EMPRESAS, HABILIDADES, PROYECTOS, OFERTAS_LABORALES, USUARIOS,
    RELACIONES_EMPRESA_OFERTA, RELACIONES_EMPRESA_PROYECTO, RELACIONES_OFERTA_HABILIDAD,
    RELACIONES_USUARIO_USUARIO, RELACIONES_USUARIO_EMPRESA, RELACIONES_USUARIO_HABILIDAD,
    RELACIONES_USUARIO_PROYECTO, RELACIONES_USUARIO_OFERTA
)

def poblar_base_datos():
    """Puebla la base de datos con nodos y relaciones según el esquema definido."""
    empresa = Empresa()
    habilidad = Habilidad()
    proyecto = Proyecto()
    oferta = OfertaLaboral()
    usuario = Usuario()
    

    map_empresas = []
    map_habilidades = []
    map_proyectos = []
    map_ofertas = []
    map_usuarios = []

    print("\n--- 2. Insertando Nodos Entidad ---")

    # Insertar Empresas
    for emp in EMPRESAS:
        nueva = empresa.crear(**emp)
        print(f"Empresa creada: {nueva}")
        map_empresas.append(nueva[0]["e"]["id"])
    print(f"✓ {len(map_empresas)} Empresas creadas.")

    # Insertar Habilidades
    for hab in HABILIDADES:
        nueva = habilidad.crear(**hab)
        map_habilidades.append(nueva[0]["h"]["id"])
    print(f"✓ {len(map_habilidades)} Habilidades creadas.")

    # Insertar Proyectos
    for proy in PROYECTOS:
        nueva = proyecto.crear(**proy)
        map_proyectos.append(nueva[0]["p"]["id"])
    print(f"✓ {len(map_proyectos)} Proyectos creados.")

    # Insertar Ofertas Laborales
    for ofe in OFERTAS_LABORALES:
        nueva = oferta.crear(**ofe)
        map_ofertas.append(nueva[0]["o"]["id"])
    print(f"✓ {len(map_ofertas)} Ofertas Laborales creadas.")

    # Insertar Usuarios
    for usr in USUARIOS:
        nueva = usuario.crear(**usr)
        map_usuarios.append(nueva[0]["u"]["id"])
    print(f"✓ {len(map_usuarios)} Usuarios creados.")

    print("\n--- 3. Creando Relaciones según el Esquema ---")

    # Empresa -> Oferta Laboral (PUBLICA)
    for idx_emp, idx_ofe in RELACIONES_EMPRESA_OFERTA:
        empresa.publica_oferta(empresa_id=map_empresas[idx_emp],oferta_id=map_ofertas[idx_ofe])

    # Empresa -> Proyecto (TIENE)
    for idx_emp, idx_proy in RELACIONES_EMPRESA_PROYECTO:
        empresa.tiene_proyecto(map_empresas[idx_emp], map_proyectos[idx_proy])

    # Oferta -> Habilidad (REQUIERE_TENER)
    for idx_ofe, idx_hab in RELACIONES_OFERTA_HABILIDAD:
       oferta.requiere_tener(map_ofertas[idx_ofe], map_habilidades[idx_hab])

    # Usuario -> Usuario (CONECTA_CON)
    for idx_u1, idx_u2 in RELACIONES_USUARIO_USUARIO:
        usuario.conecta_con(map_usuarios[idx_u1], map_usuarios[idx_u2])
    
    # Usuario -> Empresa (TRABAJA_EN)
    for idx_u, idx_emp in RELACIONES_USUARIO_EMPRESA:
        usuario.trabaja_en(map_usuarios[idx_u], map_empresas[idx_emp])

    # Usuario -> Habilidad (POSEE)
    for idx_u, idx_hab in RELACIONES_USUARIO_HABILIDAD:
        usuario.posee_habilidad(map_usuarios[idx_u], map_habilidades[idx_hab])

    # Usuario -> Proyecto (PARTICIPA_EN)
    for idx_u, idx_proy in RELACIONES_USUARIO_PROYECTO:
        usuario.participa_en(map_usuarios[idx_u], map_proyectos[idx_proy])

    # Usuario -> Oferta (SE_POSTULA_A)
    for idx_u, idx_ofe in RELACIONES_USUARIO_OFERTA:
        usuario.se_postula_a(map_usuarios[idx_u], map_ofertas[idx_ofe])

    print(" ¡Grafo completado con éxito! Todos los nodos y relaciones han sido vinculados.")

if __name__ == "__main__":
    poblar_base_datos()