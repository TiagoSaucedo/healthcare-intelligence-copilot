
import calendar
import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import text

from app.database.connection import engine


SEED = 42

DATA_INICIAL = date(2024, 1, 1)
DATA_FINAL = date(2028, 12, 31)

PROBABILIDADE_CONTA = 0.80
PROBABILIDADE_PAGAMENTO = 0.90


# Relaciona grupos de procedimentos aos tipos de prestadores
# mais adequados para o atendimento.
TIPOS_PRESTADOR_POR_GRUPO = {
    "Consultas": ["Consultório", "Clínica"],
    "Exames laboratoriais": ["Laboratório"],
    "Exames de imagem": ["Centro de Diagnóstico", "Hospital"],
    "Terapias": ["Clínica", "Consultório"],
    "Cirurgias": ["Hospital"],
    "Internações": ["Hospital"],
    "Urgência e emergência": ["Pronto Atendimento", "Hospital"],
    "Procedimentos ambulatoriais": ["Clínica", "Consultório", "Hospital"],
}


def adicionar_meses(data: date) -> date:
    """Retorna o primeiro dia do mês seguinte."""
    if data.month == 12:
        return date(data.year + 1, 1, 1)

    return date(data.year, data.month + 1, 1)


def gerar_data_atendimento(
    competencia: date,
    rng: random.Random,
) -> date:
    ultimo_dia = calendar.monthrange(
        competencia.year,
        competencia.month,
    )[1]

    dia = rng.randint(1, ultimo_dia)

    return date(
        competencia.year,
        competencia.month,
        dia,
    )


def buscar_versao_beneficiario(
    codigo_beneficiario: str,
    data_atendimento: date,
    beneficiarios_por_codigo: dict,
) -> dict | None:
    versoes = beneficiarios_por_codigo.get(
        codigo_beneficiario,
        [],
    )

    versoes_validas = [
        versao
        for versao in versoes
        if versao["data_inicio_vigencia"] <= data_atendimento
        and (
            versao["data_fim_vigencia"] is None
            or versao["data_fim_vigencia"] >= data_atendimento
        )
    ]

    if len(versoes_validas) > 1:
        raise ValueError(
            f"Mais de uma versão válida para {codigo_beneficiario} "
            f"em {data_atendimento}."
        )

    return versoes_validas[0] if versoes_validas else None


def carregar_dimensoes() -> dict:
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

        prestadores = connection.execute(
            text(
                """
                SELECT
                    id_prestador,
                    tipo_prestador
                FROM dim_prestador
                """
            )
        ).mappings().all()

        procedimentos = connection.execute(
            text(
                """
                SELECT
                    id_procedimento,
                    grupo_procedimento,
                    tipo_procedimento
                FROM dim_procedimento
                """
            )
        ).mappings().all()

        tempos = connection.execute(
            text(
                """
                SELECT id_tempo, data
                FROM dim_tempo
                WHERE data BETWEEN :inicio AND :fim
                """
            ),
            {
                "inicio": DATA_INICIAL,
                "fim": DATA_FINAL,
            },
        ).mappings().all()

    beneficiarios_por_codigo = {}

    for beneficiario in beneficiarios:
        codigo = beneficiario["codigo_beneficiario"]

        beneficiarios_por_codigo.setdefault(
            codigo,
            [],
        ).append(beneficiario)

    prestadores_por_tipo = {}

    for prestador in prestadores:
        prestadores_por_tipo.setdefault(
            prestador["tipo_prestador"],
            [],
        ).append(prestador)

    procedimentos_por_grupo = {}

    for procedimento in procedimentos:
        procedimentos_por_grupo.setdefault(
            procedimento["grupo_procedimento"],
            [],
        ).append(procedimento)

    return {
        "beneficiarios": beneficiarios_por_codigo,
        "prestadores": prestadores_por_tipo,
        "procedimentos": procedimentos_por_grupo,
        "tempos": {
            registro["data"]: registro["id_tempo"]
            for registro in tempos
        },
    }


def gerar_despesas() -> list[dict]:
    rng = random.Random(SEED)

    dimensoes = carregar_dimensoes()

    beneficiarios = dimensoes["beneficiarios"]
    prestadores = dimensoes["prestadores"]
    procedimentos = dimensoes["procedimentos"]
    tempos = dimensoes["tempos"]

    with engine.connect() as connection:
        receitas = connection.execute(
            text(
                """
                SELECT
                    b.codigo_beneficiario,
                    r.data_reconhecimento AS competencia,
                    r.valor_receita
                FROM fato_receita r
                JOIN dim_beneficiario b
                    ON b.id_beneficiario = r.id_beneficiario
                ORDER BY
                    b.codigo_beneficiario,
                    r.data_reconhecimento
                """
            )
        ).mappings().all()

    if not receitas:
        raise ValueError(
            "A fato_receita está vazia. "
            "Carregue as receitas antes das despesas."
        )

    despesas = []
    numero_conta = 0

    for receita in receitas:

        if rng.random() > PROBABILIDADE_CONTA:
            continue

        competencia = receita["competencia"]

        data_atendimento = gerar_data_atendimento(
            competencia,
            rng,
        )

        codigo_beneficiario = receita["codigo_beneficiario"]

        versao = buscar_versao_beneficiario(
            codigo_beneficiario,
            data_atendimento,
            beneficiarios,
        )

        if versao is None:
            continue

        id_tempo_atendimento = tempos.get(data_atendimento)

        if id_tempo_atendimento is None:
            raise ValueError(
                f"Data de atendimento {data_atendimento} "
                "não encontrada em dim_tempo."
            )

        # Uma conta pode possuir múltiplos itens.
        quantidade_itens = rng.randint(1, 3)

        # O valor total apresentado varia conforme
        # a receita mensal do beneficiário.
        fator_custo = Decimal(
            str(round(rng.uniform(0.75, 1.15), 4))
        )

        valor_total = (
            Decimal(receita["valor_receita"]) * fator_custo
        ).quantize(Decimal("0.01"))

        # Distribui o valor total entre os itens.
        pesos = [
            rng.uniform(0.5, 1.5)
            for _ in range(quantidade_itens)
        ]

        soma_pesos = sum(pesos)

        valores_itens = []

        valor_distribuido = Decimal("0.00")

        for indice, peso in enumerate(pesos):

            if indice == quantidade_itens - 1:
                valor_item = valor_total - valor_distribuido
            else:
                valor_item = (
                    valor_total * Decimal(str(peso / soma_pesos))
                ).quantize(Decimal("0.01"))

                valor_distribuido += valor_item

            valores_itens.append(valor_item)

        # Define se a conta será paga.
        pagamento_realizado = (
            rng.random() < PROBABILIDADE_PAGAMENTO
        )

        if pagamento_realizado:
            dias_ate_pagamento = rng.randint(5, 60)

            data_pagamento = (
                data_atendimento
                + timedelta(days=dias_ate_pagamento)
            )

            # Não extrapolamos o calendário disponível.
            if data_pagamento > DATA_FINAL:
                pagamento_realizado = False
                data_pagamento = None
        else:
            data_pagamento = None

        if pagamento_realizado:
            id_tempo_pagamento = tempos.get(data_pagamento)

            if id_tempo_pagamento is None:
                raise ValueError(
                    f"Data de pagamento {data_pagamento} "
                    "não encontrada em dim_tempo."
                )

            fator_pagamento = Decimal(
                str(round(rng.uniform(0.85, 1.00), 4))
            )
        else:
            id_tempo_pagamento = None
            fator_pagamento = Decimal("0.00")

        numero_conta += 1

        identificador_conta = (
            f"CTA-{codigo_beneficiario}-"
            f"{competencia.strftime('%Y%m')}"
        )

        for indice, valor_item in enumerate(valores_itens, start=1):

            procedimento = None
            prestador = None

            # Seleciona um grupo de procedimento e um prestador
            # compatível com aquele grupo.
            grupos_disponiveis = [
                grupo
                for grupo, tipos in TIPOS_PRESTADOR_POR_GRUPO.items()
                if procedimentos.get(grupo)
                and any(
                    prestadores.get(tipo)
                    for tipo in tipos
                )
            ]

            grupo = rng.choice(grupos_disponiveis)

            procedimento = rng.choice(
                procedimentos[grupo]
            )

            tipos_compativeis = [
                tipo
                for tipo in TIPOS_PRESTADOR_POR_GRUPO[grupo]
                if prestadores.get(tipo)
            ]

            tipo_prestador = rng.choice(tipos_compativeis)

            prestador = rng.choice(
                prestadores[tipo_prestador]
            )

            valor_pago = (
                valor_item * fator_pagamento
            ).quantize(Decimal("0.01"))

            quantidade = rng.randint(1, 3)

            despesas.append(
                {
                    "id_beneficiario": versao["id_beneficiario"],
                    "id_prestador": prestador["id_prestador"],
                    "id_procedimento": procedimento["id_procedimento"],
                    "id_tempo_atendimento": id_tempo_atendimento,
                    "id_tempo_pagamento": id_tempo_pagamento,
                    "numero_conta": identificador_conta,
                    "numero_item": indice,
                    "quantidade": quantidade,
                    "valor_apresentado": valor_item,
                    "valor_pago": valor_pago,
                    "data_atendimento": data_atendimento,
                    "data_pagamento": data_pagamento,
                }
            )

    return despesas


def carregar_despesas() -> None:
    despesas = gerar_despesas()

    with engine.begin() as connection:

        contas_existentes = {
            (registro[0], registro[1])
            for registro in connection.execute(
                text(
                    """
                    SELECT numero_conta, numero_item
                    FROM fato_despesa_assistencial
                    """
                )
            ).all()
        }

        novas_despesas = [
            despesa
            for despesa in despesas
            if (
                despesa["numero_conta"],
                despesa["numero_item"],
            ) not in contas_existentes
        ]

        if novas_despesas:
            connection.execute(
                text(
                    """
                    INSERT INTO fato_despesa_assistencial (
                        id_beneficiario,
                        id_prestador,
                        id_procedimento,
                        id_tempo_atendimento,
                        id_tempo_pagamento,
                        numero_conta,
                        numero_item,
                        quantidade,
                        valor_apresentado,
                        valor_pago,
                        data_atendimento,
                        data_pagamento
                    )
                    VALUES (
                        :id_beneficiario,
                        :id_prestador,
                        :id_procedimento,
                        :id_tempo_atendimento,
                        :id_tempo_pagamento,
                        :numero_conta,
                        :numero_item,
                        :quantidade,
                        :valor_apresentado,
                        :valor_pago,
                        :data_atendimento,
                        :data_pagamento
                    )
                    """
                ),
                novas_despesas,
            )

    print("Carga de despesas concluída.")
    print(f"Itens gerados: {len(despesas)}")
    print(f"Itens inseridos: {len(novas_despesas)}")
    print(f"Itens já existentes: {len(contas_existentes)}")
    print(
        f"Contas geradas: "
        f"{len(set(d['numero_conta'] for d in despesas))}"
    )


if __name__ == "__main__":
    carregar_despesas()
