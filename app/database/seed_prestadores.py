
"""
Healthcare Intelligence Copilot
Geração de prestadores sintéticos.
"""

import random

from sqlalchemy import text

from app.database.connection import engine


# ============================================================
# CONFIGURAÇÕES
# ============================================================

SEED = 42
TOTAL_PRESTADORES = 150

TIPOS_PRESTADOR = [
    "Hospital",
    "Clínica",
    "Laboratório",
    "Centro de Diagnóstico",
    "Consultório",
    "Pronto Atendimento",
]

ESPECIALIDADES = [
    "Cardiologia",
    "Ortopedia",
    "Pediatria",
    "Oncologia",
    "Neurologia",
    "Ginecologia",
    "Oftalmologia",
    "Endocrinologia",
    "Dermatologia",
    "Radiologia",
    "Análises Clínicas",
    "Clínica Geral",
    "Cirurgia Geral",
    "Urologia",
    "Gastroenterologia",
    "Multiespecialidade",
]

LOCALIDADES = [
    ("Campo Grande", "MS"),
    ("Dourados", "MS"),
    ("Três Lagoas", "MS"),
    ("Corumbá", "MS"),
    ("Ponta Porã", "MS"),
    ("São Paulo", "SP"),
    ("Curitiba", "PR"),
    ("Goiânia", "GO"),
    ("Brasília", "DF"),
    ("Cuiabá", "MT"),
]

PREFIXOS_NOMES = [
    "Vida",
    "São Lucas",
    "Santa Clara",
    "Nova Saúde",
    "Bom Cuidado",
    "Integra",
    "Med",
    "Excelência",
    "Regional",
    "Prime",
    "Esperança",
    "Central",
]

SUFIXOS_NOMES = [
    "Saúde",
    "Medicina",
    "Hospital",
    "Clínica",
    "Diagnósticos",
    "Assistência Médica",
    "Centro Médico",
    "Especialidades",
]


# ============================================================
# GERAÇÃO
# ============================================================

def gerar_prestadores() -> list[dict]:
    """Gera prestadores fictícios com resultado reproduzível."""

    rng = random.Random(SEED)
    registros = []

    for numero in range(1, TOTAL_PRESTADORES + 1):

        tipo = rng.choice(TIPOS_PRESTADOR)
        cidade, estado = rng.choice(LOCALIDADES)

        prefixo = rng.choice(PREFIXOS_NOMES)
        sufixo = rng.choice(SUFIXOS_NOMES)

        nome = f"{prefixo} {sufixo} {numero:03d}"

        if tipo in ("Hospital", "Pronto Atendimento"):
            especialidade = "Multiespecialidade"
        else:
            especialidade = rng.choice(ESPECIALIDADES)

        registros.append({
            "codigo_prestador": f"PREST{numero:04d}",
            "nome_prestador": nome,
            "tipo_prestador": tipo,
            "cidade": cidade,
            "estado": estado,
            "especialidade": especialidade,
        })

    return registros


# ============================================================
# PERSISTÊNCIA
# ============================================================

def carregar_prestadores() -> None:
    """Insere prestadores sem duplicar códigos existentes."""

    registros = gerar_prestadores()

    sql_existentes = text("""
        SELECT codigo_prestador
        FROM dim_prestador
    """)

    sql_insert = text("""
        INSERT INTO dim_prestador (
            codigo_prestador,
            nome_prestador,
            tipo_prestador,
            cidade,
            estado,
            especialidade
        )
        VALUES (
            :codigo_prestador,
            :nome_prestador,
            :tipo_prestador,
            :cidade,
            :estado,
            :especialidade
        )
    """)

    with engine.begin() as connection:

        codigos_existentes = set(
            connection.execute(sql_existentes).scalars().all()
        )

        registros_novos = [
            registro
            for registro in registros
            if registro["codigo_prestador"] not in codigos_existentes
        ]

        if registros_novos:
            connection.execute(sql_insert, registros_novos)

    print("Carga de prestadores concluída.")
    print(f"Prestadores gerados: {len(registros)}")
    print(f"Prestadores inseridos: {len(registros_novos)}")
    print(f"Códigos já existentes: {len(codigos_existentes)}")


if __name__ == "__main__":
    carregar_prestadores()
