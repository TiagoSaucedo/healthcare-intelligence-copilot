
import random

from sqlalchemy import text

from app.database.connection import engine


SEED = 42
TOTAL_PROCEDIMENTOS = 200

random.seed(SEED)


PROCEDIMENTOS = {
    "Consultas": {
        "categoria": "Ambulatorial",
        "tipo": "Consulta",
        "descricoes": [
            "Consulta em cardiologia",
            "Consulta em endocrinologia",
            "Consulta em ortopedia",
            "Consulta em neurologia",
            "Consulta em ginecologia",
            "Consulta em pediatria",
            "Consulta em dermatologia",
            "Consulta em psiquiatria",
            "Consulta em clínica médica",
            "Consulta em oftalmologia",
        ],
    },
    "Exames laboratoriais": {
        "categoria": "Diagnóstico",
        "tipo": "Exame",
        "descricoes": [
            "Hemograma completo",
            "Glicemia em jejum",
            "Hemoglobina glicada",
            "Colesterol total",
            "Perfil lipídico",
            "Creatinina",
            "Ureia",
            "TSH",
            "T4 livre",
            "Exame de urina",
            "Dosagem de vitamina D",
            "Dosagem de vitamina B12",
            "Transaminases",
            "Proteína C reativa",
            "Coagulograma",
        ],
    },
    "Exames de imagem": {
        "categoria": "Diagnóstico",
        "tipo": "Exame",
        "descricoes": [
            "Ultrassonografia abdominal",
            "Ultrassonografia obstétrica",
            "Raio-X de tórax",
            "Raio-X de coluna",
            "Tomografia de crânio",
            "Tomografia de tórax",
            "Ressonância magnética de joelho",
            "Ressonância magnética de coluna",
            "Mamografia",
            "Ecocardiograma",
            "Densitometria óssea",
            "Eletrocardiograma",
        ],
    },
    "Terapias": {
        "categoria": "Tratamento",
        "tipo": "Terapia",
        "descricoes": [
            "Sessão de fisioterapia",
            "Sessão de psicoterapia",
            "Sessão de fonoaudiologia",
            "Sessão de terapia ocupacional",
            "Sessão de fisioterapia respiratória",
            "Sessão de reabilitação motora",
        ],
    },
    "Cirurgias": {
        "categoria": "Cirúrgico",
        "tipo": "Cirurgia",
        "descricoes": [
            "Colecistectomia",
            "Herniorrafia",
            "Apendicectomia",
            "Artroscopia de joelho",
            "Cirurgia de catarata",
            "Histerectomia",
            "Cirurgia de varizes",
            "Amigdalectomia",
        ],
    },
    "Internações": {
        "categoria": "Hospitalar",
        "tipo": "Internação",
        "descricoes": [
            "Internação clínica",
            "Internação cirúrgica",
            "Internação em UTI adulto",
            "Internação em UTI pediátrica",
            "Internação obstétrica",
            "Internação neonatal",
        ],
    },
    "Urgência e emergência": {
        "categoria": "Urgência",
        "tipo": "Urgência",
        "descricoes": [
            "Atendimento em pronto-socorro",
            "Atendimento de urgência cardiológica",
            "Atendimento de urgência ortopédica",
            "Atendimento de urgência pediátrica",
            "Atendimento de urgência clínica",
        ],
    },
    "Procedimentos ambulatoriais": {
        "categoria": "Ambulatorial",
        "tipo": "Procedimento",
        "descricoes": [
            "Curativo simples",
            "Retirada de pontos",
            "Pequena cirurgia ambulatorial",
            "Infiltração articular",
            "Endoscopia digestiva",
            "Colonoscopia",
            "Biópsia ambulatorial",
            "Administração de medicamento",
        ],
    },
}


def gerar_procedimentos() -> list[dict]:
    procedimentos = []
    grupos = list(PROCEDIMENTOS.keys())

    for i in range(1, TOTAL_PROCEDIMENTOS + 1):
        grupo = random.choice(grupos)
        configuracao = PROCEDIMENTOS[grupo]
        descricao_base = random.choice(configuracao["descricoes"])

        procedimentos.append(
            {
                "codigo_procedimento": f"PROC{i:04d}",
                "descricao": f"{descricao_base} - modalidade {i:03d}",
                "grupo_procedimento": grupo,
                "categoria": configuracao["categoria"],
                "tipo_procedimento": configuracao["tipo"],
            }
        )

    return procedimentos


def carregar_procedimentos() -> None:
    procedimentos = gerar_procedimentos()

    with engine.begin() as connection:
        codigos_existentes = set(
            connection.execute(
                text("SELECT codigo_procedimento FROM dim_procedimento")
            ).scalars().all()
        )

        novos_procedimentos = [
            procedimento
            for procedimento in procedimentos
            if procedimento["codigo_procedimento"] not in codigos_existentes
        ]

        if novos_procedimentos:
            connection.execute(
                text(
                    """
                    INSERT INTO dim_procedimento (
                        codigo_procedimento,
                        descricao,
                        grupo_procedimento,
                        categoria,
                        tipo_procedimento
                    )
                    VALUES (
                        :codigo_procedimento,
                        :descricao,
                        :grupo_procedimento,
                        :categoria,
                        :tipo_procedimento
                    )
                    """
                ),
                novos_procedimentos,
            )

    print("Carga de procedimentos concluída.")
    print(f"Procedimentos gerados: {len(procedimentos)}")
    print(f"Procedimentos inseridos: {len(novos_procedimentos)}")
    print(f"Códigos já existentes: {len(codigos_existentes)}")


if __name__ == "__main__":
    carregar_procedimentos()
