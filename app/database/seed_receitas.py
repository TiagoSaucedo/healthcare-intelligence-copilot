
import random
from datetime import date
from decimal import Decimal

from sqlalchemy import text

from app.database.connection import engine


SEED = 42

DATA_INICIAL = date(2024, 1, 1)
DATA_FINAL = date(2028, 12, 31)


def gerar_competencias() -> list[date]:
    competencias = []
    atual = DATA_INICIAL

    while atual <= DATA_FINAL:
        competencias.append(atual)

        if atual.month == 12:
            atual = date(atual.year + 1, 1, 1)
        else:
            atual = date(atual.year, atual.month + 1, 1)

    return competencias


def calcular_valor_receita(
    tipo_contrato: str,
    modalidade: str,
    rng: random.Random,
) -> Decimal:
    # Valores mensais sintéticos por beneficiário.
    faixas = {
        "Básico": (18000, 35000),
        "Intermediário": (30000, 55000),
        "Premium": (45000, 80000),
    }

    valor_minimo, valor_maximo = faixas.get(
        tipo_contrato,
        (25000, 45000),
    )

    multiplicadores = {
        "Individual": 1.05,
        "Familiar": 0.95,
        "Empresarial": 0.90,
        "Coletivo por adesão": 0.95,
    }

    multiplicador = multiplicadores.get(modalidade, 1.0)

    valor_centavos = rng.randint(valor_minimo, valor_maximo)
    valor = Decimal(valor_centavos) * Decimal(str(multiplicador))

    return (valor / Decimal("100")).quantize(Decimal("0.01"))


def gerar_receitas() -> list[dict]:
    rng = random.Random(SEED)

    with engine.connect() as connection:
        beneficiarios = connection.execute(
            text(
                """
                SELECT
                    id_beneficiario,
                    codigo_beneficiario,
                    data_inicio_vigencia,
                    data_fim_vigencia
                FROM dim_beneficiario
                ORDER BY codigo_beneficiario, data_inicio_vigencia
                """
            )
        ).mappings().all()

        contratos = connection.execute(
            text(
                """
                SELECT
                    id_contrato,
                    codigo_contrato,
                    modalidade,
                    tipo_contrato
                FROM dim_contrato
                ORDER BY codigo_contrato
                """
            )
        ).mappings().all()

        tempos = connection.execute(
            text(
                """
                SELECT id_tempo, data
                FROM dim_tempo
                WHERE EXTRACT(DAY FROM data) = 1
                  AND data BETWEEN :inicio AND :fim
                """
            ),
            {
                "inicio": DATA_INICIAL,
                "fim": DATA_FINAL,
            },
        ).mappings().all()

    if not beneficiarios:
        raise ValueError("A dimensão dim_beneficiario está vazia.")

    if not contratos:
        raise ValueError("A dimensão dim_contrato está vazia.")

    mapa_tempo = {registro["data"]: registro["id_tempo"] for registro in tempos}

    # Agrupa todas as versões de cada beneficiário.
    beneficiarios_por_codigo = {}

    for beneficiario in beneficiarios:
        codigo = beneficiario["codigo_beneficiario"]

        beneficiarios_por_codigo.setdefault(codigo, []).append(
            beneficiario
        )

    competencias = gerar_competencias()
    receitas = []

    for codigo, versoes in beneficiarios_por_codigo.items():

        # O contrato permanece associado ao beneficiário
        # durante todo o período sintético.
        contrato = rng.choice(contratos)

        for competencia in competencias:

            versoes_validas = [
                versao
                for versao in versoes
                if versao["data_inicio_vigencia"] <= competencia
                and (
                    versao["data_fim_vigencia"] is None
                    or versao["data_fim_vigencia"] >= competencia
                )
            ]

            if len(versoes_validas) > 1:
                raise ValueError(
                    f"Mais de uma versão válida para {codigo} "
                    f"na competência {competencia}."
                )

            if not versoes_validas:
                continue

            if competencia not in mapa_tempo:
                raise ValueError(
                    f"Competência {competencia} não encontrada em dim_tempo."
                )

            versao = versoes_validas[0]

            valor_receita = calcular_valor_receita(
                contrato["tipo_contrato"],
                contrato["modalidade"],
                rng,
            )

            receitas.append(
                {
                    "id_beneficiario": versao["id_beneficiario"],
                    "id_contrato": contrato["id_contrato"],
                    "id_tempo_competencia": mapa_tempo[competencia],
                    "numero_lancamento": (
                        f"REC-{codigo}-{competencia.strftime('%Y%m')}"
                    ),
                    "valor_receita": valor_receita,
                    "data_reconhecimento": competencia,
                }
            )

    return receitas


def carregar_receitas() -> None:
    receitas = gerar_receitas()

    with engine.begin() as connection:

        lancamentos_existentes = set(
            connection.execute(
                text(
                    """
                    SELECT numero_lancamento
                    FROM fato_receita
                    """
                )
            ).scalars().all()
        )

        novas_receitas = [
            receita
            for receita in receitas
            if receita["numero_lancamento"] not in lancamentos_existentes
        ]

        if novas_receitas:
            connection.execute(
                text(
                    """
                    INSERT INTO fato_receita (
                        id_beneficiario,
                        id_contrato,
                        id_tempo_competencia,
                        numero_lancamento,
                        valor_receita,
                        data_reconhecimento
                    )
                    VALUES (
                        :id_beneficiario,
                        :id_contrato,
                        :id_tempo_competencia,
                        :numero_lancamento,
                        :valor_receita,
                        :data_reconhecimento
                    )
                    """
                ),
                novas_receitas,
            )

    print("Carga de receitas concluída.")
    print(f"Receitas geradas: {len(receitas)}")
    print(f"Receitas inseridas: {len(novas_receitas)}")
    print(f"Lançamentos já existentes: {len(lancamentos_existentes)}")


if __name__ == "__main__":
    carregar_receitas()
