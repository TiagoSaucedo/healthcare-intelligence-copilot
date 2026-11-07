
import random

from sqlalchemy import text

from app.database.connection import engine


SEED = 42
TOTAL_CONTRATOS = 50

random.seed(SEED)


MODALIDADES = [
    "Individual",
    "Familiar",
    "Empresarial",
    "Coletivo por adesão",
]

COBERTURAS = [
    "Ambulatorial",
    "Hospitalar",
    "Hospitalar com obstetrícia",
    "Referência",
]

ACOMODACOES = [
    "Enfermaria",
    "Apartamento",
]

TIPOS_CONTRATO = [
    "Básico",
    "Intermediário",
    "Premium",
]


def gerar_contratos() -> list[dict]:
    contratos = []

    for i in range(1, TOTAL_CONTRATOS + 1):
        modalidade = random.choice(MODALIDADES)
        cobertura = random.choice(COBERTURAS)

        # Contratos exclusivamente ambulatoriais não possuem acomodação hospitalar.
        if cobertura == "Ambulatorial":
            acomodacao = "Não se aplica"
        else:
            acomodacao = random.choice(ACOMODACOES)

        tipo_contrato = random.choice(TIPOS_CONTRATO)

        contratos.append(
            {
                "codigo_contrato": f"CONT{i:04d}",
                "modalidade": modalidade,
                "cobertura": cobertura,
                "acomodacao": acomodacao,
                "tipo_contrato": tipo_contrato,
            }
        )

    return contratos


def carregar_contratos() -> None:
    contratos = gerar_contratos()

    with engine.begin() as connection:
        codigos_existentes = set(
            connection.execute(
                text("SELECT codigo_contrato FROM dim_contrato")
            ).scalars().all()
        )

        novos_contratos = [
            contrato
            for contrato in contratos
            if contrato["codigo_contrato"] not in codigos_existentes
        ]

        if novos_contratos:
            connection.execute(
                text(
                    """
                    INSERT INTO dim_contrato (
                        codigo_contrato,
                        modalidade,
                        cobertura,
                        acomodacao,
                        tipo_contrato
                    )
                    VALUES (
                        :codigo_contrato,
                        :modalidade,
                        :cobertura,
                        :acomodacao,
                        :tipo_contrato
                    )
                    """
                ),
                novos_contratos,
            )

    print("Carga de contratos concluída.")
    print(f"Contratos gerados: {len(contratos)}")
    print(f"Contratos inseridos: {len(novos_contratos)}")
    print(f"Códigos já existentes: {len(codigos_existentes)}")


if __name__ == "__main__":
    carregar_contratos()
