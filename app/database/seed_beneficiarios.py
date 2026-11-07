
"""
Healthcare Intelligence Copilot
Geração de beneficiários sintéticos com histórico SCD Tipo 2.
"""

import random
from datetime import date, timedelta

from sqlalchemy import text

from app.database.connection import engine


# ============================================================
# CONFIGURAÇÕES
# ============================================================

SEED = 42
TOTAL_BENEFICIARIOS = 1000

DATA_INICIAL = date(2024, 1, 1)
DATA_FINAL = date(2028, 12, 31)

PERCENTUAL_COM_HISTORICO = 0.25
PERCENTUAL_COM_DUAS_ALTERACOES = 0.05

FAIXAS_ETARIAS = [
    "0-18",
    "19-23",
    "24-28",
    "29-33",
    "34-38",
    "39-43",
    "44-48",
    "49-53",
    "54-58",
    "59+",
]

SEXOS = ["Feminino", "Masculino", "Não informado"]

TIPOS_BENEFICIARIO = ["Titular", "Dependente"]

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


# ============================================================
# GERAÇÃO DOS REGISTROS
# ============================================================

def gerar_data_aleatoria(
    rng: random.Random,
    inicio: date,
    fim: date,
) -> date:
    """Gera uma data aleatória dentro de um intervalo."""
    intervalo = (fim - inicio).days
    return inicio + timedelta(days=rng.randint(0, intervalo))



def gerar_historico_beneficiario(
    rng: random.Random,
    codigo: str,
) -> list[dict]:
    """Gera versões históricas válidas de um beneficiário."""

    sorteio = rng.random()

    if sorteio < PERCENTUAL_COM_DUAS_ALTERACOES:
        quantidade_versoes = 3
    elif sorteio < PERCENTUAL_COM_HISTORICO:
        quantidade_versoes = 2
    else:
        quantidade_versoes = 1

    # Reserva pelo menos 90 dias entre cada versão.
    dias_reservados = 90 * (quantidade_versoes - 1)

    limite_inicio = DATA_FINAL - timedelta(days=dias_reservados)

    inicio = gerar_data_aleatoria(
        rng,
        DATA_INICIAL,
        limite_inicio,
    )

    datas_inicio = [inicio]

    for indice in range(1, quantidade_versoes):
        ultima_data = datas_inicio[-1]

        limite_maximo = DATA_FINAL - timedelta(
            days=90 * (quantidade_versoes - indice - 1)
        )

        nova_data = gerar_data_aleatoria(
            rng,
            ultima_data + timedelta(days=90),
            limite_maximo,
        )

        datas_inicio.append(nova_data)

    faixa_etaria = rng.choice(FAIXAS_ETARIAS)
    sexo = rng.choice(SEXOS)
    cidade, estado = rng.choice(LOCALIDADES)
    tipo = rng.choice(TIPOS_BENEFICIARIO)

    historico = []

    for indice, data_inicio in enumerate(datas_inicio):

        if indice > 0:
            if rng.choice(["cidade", "faixa_etaria"]) == "cidade":
                nova_localidade = rng.choice(
                    [
                        local
                        for local in LOCALIDADES
                        if local != (cidade, estado)
                    ]
                )
                cidade, estado = nova_localidade
            else:
                faixa_etaria = rng.choice(
                    [
                        faixa
                        for faixa in FAIXAS_ETARIAS
                        if faixa != faixa_etaria
                    ]
                )

        ativo_atual = indice == quantidade_versoes - 1

        data_fim = (
            None
            if ativo_atual
            else datas_inicio[indice + 1] - timedelta(days=1)
        )

        historico.append({
            "codigo_beneficiario": codigo,
            "faixa_etaria": faixa_etaria,
            "sexo": sexo,
            "cidade": cidade,
            "estado": estado,
            "tipo_beneficiario": tipo,
            "data_inicio_vigencia": data_inicio,
            "data_fim_vigencia": data_fim,
            "ativo_atual": ativo_atual,
        })

    return historico



def gerar_beneficiarios() -> list[dict]:
    """Gera todos os beneficiários com resultado reproduzível."""

    rng = random.Random(SEED)
    registros = []

    for numero in range(1, TOTAL_BENEFICIARIOS + 1):
        codigo = f"BEN{numero:06d}"

        historico = gerar_historico_beneficiario(
            rng,
            codigo,
        )

        registros.extend(historico)

    return registros


# ============================================================
# PERSISTÊNCIA NO POSTGRESQL
# ============================================================

def carregar_beneficiarios() -> None:
    """Insere os beneficiários sem duplicar códigos existentes."""

    registros = gerar_beneficiarios()

    sql_existentes = text("""
        SELECT DISTINCT codigo_beneficiario
        FROM dim_beneficiario
    """)

    sql_insert = text("""
        INSERT INTO dim_beneficiario (
            codigo_beneficiario,
            faixa_etaria,
            sexo,
            cidade,
            estado,
            tipo_beneficiario,
            data_inicio_vigencia,
            data_fim_vigencia,
            ativo_atual
        )
        VALUES (
            :codigo_beneficiario,
            :faixa_etaria,
            :sexo,
            :cidade,
            :estado,
            :tipo_beneficiario,
            :data_inicio_vigencia,
            :data_fim_vigencia,
            :ativo_atual
        )
    """)

    with engine.begin() as connection:

        codigos_existentes = set(
            connection.execute(sql_existentes).scalars().all()
        )

        registros_novos = [
            registro
            for registro in registros
            if registro["codigo_beneficiario"]
            not in codigos_existentes
        ]

        if registros_novos:
            connection.execute(sql_insert, registros_novos)

    total_codigos = len({
        registro["codigo_beneficiario"]
        for registro in registros
    })

    print("Carga de beneficiários concluída.")
    print(f"Beneficiários gerados: {total_codigos}")
    print(f"Versões cadastrais geradas: {len(registros)}")
    print(f"Versões inseridas: {len(registros_novos)}")
    print(f"Códigos já existentes: {len(codigos_existentes)}")


if __name__ == "__main__":
    carregar_beneficiarios()
