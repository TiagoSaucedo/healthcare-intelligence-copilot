
-- ============================================================
-- HEALTHCARE INTELLIGENCE COPILOT
-- 001 - Criação do modelo dimensional
-- PostgreSQL 17
-- ============================================================

-- DIMENSÃO: TEMPO
CREATE TABLE IF NOT EXISTS dim_tempo (
    id_tempo INTEGER PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    ano SMALLINT NOT NULL,
    trimestre SMALLINT NOT NULL,
    mes SMALLINT NOT NULL,
    nome_mes VARCHAR(20) NOT NULL,
    ano_mes CHAR(7) NOT NULL,

    CONSTRAINT ck_tempo_trimestre
        CHECK (trimestre BETWEEN 1 AND 4),

    CONSTRAINT ck_tempo_mes
        CHECK (mes BETWEEN 1 AND 12)
);

-- DIMENSÃO: BENEFICIÁRIO
CREATE TABLE IF NOT EXISTS dim_beneficiario (
    id_beneficiario BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_beneficiario VARCHAR(50) NOT NULL UNIQUE,
    faixa_etaria VARCHAR(30),
    sexo VARCHAR(20),
    cidade VARCHAR(100),
    estado CHAR(2),
    tipo_beneficiario VARCHAR(30),
    data_inicio_vigencia DATE,
    data_fim_vigencia DATE,

    CONSTRAINT ck_beneficiario_vigencia
        CHECK (
            data_fim_vigencia IS NULL
            OR data_inicio_vigencia IS NULL
            OR data_fim_vigencia >= data_inicio_vigencia
        )
);

-- DIMENSÃO: PRESTADOR
CREATE TABLE IF NOT EXISTS dim_prestador (
    id_prestador BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_prestador VARCHAR(50) NOT NULL UNIQUE,
    nome_prestador VARCHAR(150) NOT NULL,
    tipo_prestador VARCHAR(50),
    cidade VARCHAR(100),
    estado CHAR(2),
    especialidade VARCHAR(100)
);

-- DIMENSÃO: PROCEDIMENTO
CREATE TABLE IF NOT EXISTS dim_procedimento (
    id_procedimento BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_procedimento VARCHAR(50) NOT NULL UNIQUE,
    descricao VARCHAR(200) NOT NULL,
    grupo_procedimento VARCHAR(100),
    categoria VARCHAR(100),
    tipo_procedimento VARCHAR(50)
);

-- DIMENSÃO: CONTRATO
CREATE TABLE IF NOT EXISTS dim_contrato (
    id_contrato BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_contrato VARCHAR(50) NOT NULL UNIQUE,
    modalidade VARCHAR(50),
    cobertura VARCHAR(100),
    acomodacao VARCHAR(50),
    tipo_contrato VARCHAR(50)
);

-- FATO: RECEITA
CREATE TABLE IF NOT EXISTS fato_receita (
    id_receita BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_beneficiario BIGINT NOT NULL,
    id_contrato BIGINT NOT NULL,
    id_tempo_competencia INTEGER NOT NULL,
    numero_lancamento VARCHAR(50),
    valor_receita NUMERIC(15,2) NOT NULL,
    data_reconhecimento DATE NOT NULL,

    CONSTRAINT fk_receita_beneficiario
        FOREIGN KEY (id_beneficiario)
        REFERENCES dim_beneficiario (id_beneficiario),

    CONSTRAINT fk_receita_contrato
        FOREIGN KEY (id_contrato)
        REFERENCES dim_contrato (id_contrato),

    CONSTRAINT fk_receita_tempo
        FOREIGN KEY (id_tempo_competencia)
        REFERENCES dim_tempo (id_tempo),

    CONSTRAINT ck_receita_valor
        CHECK (valor_receita >= 0)
);

-- FATO: DESPESA ASSISTENCIAL
CREATE TABLE IF NOT EXISTS fato_despesa_assistencial (
    id_despesa BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_beneficiario BIGINT NOT NULL,
    id_prestador BIGINT NOT NULL,
    id_procedimento BIGINT NOT NULL,
    id_tempo_atendimento INTEGER NOT NULL,
    id_tempo_pagamento INTEGER,
    numero_conta VARCHAR(50) NOT NULL,
    numero_item INTEGER NOT NULL,
    quantidade NUMERIC(12,2) NOT NULL,
    valor_apresentado NUMERIC(15,2) NOT NULL,
    valor_pago NUMERIC(15,2) NOT NULL DEFAULT 0,
    data_atendimento DATE NOT NULL,
    data_pagamento DATE,

    CONSTRAINT fk_despesa_beneficiario
        FOREIGN KEY (id_beneficiario)
        REFERENCES dim_beneficiario (id_beneficiario),

    CONSTRAINT fk_despesa_prestador
        FOREIGN KEY (id_prestador)
        REFERENCES dim_prestador (id_prestador),

    CONSTRAINT fk_despesa_procedimento
        FOREIGN KEY (id_procedimento)
        REFERENCES dim_procedimento (id_procedimento),

    CONSTRAINT fk_despesa_tempo_atendimento
        FOREIGN KEY (id_tempo_atendimento)
        REFERENCES dim_tempo (id_tempo),

    CONSTRAINT fk_despesa_tempo_pagamento
        FOREIGN KEY (id_tempo_pagamento)
        REFERENCES dim_tempo (id_tempo),

    CONSTRAINT uq_despesa_conta_item
        UNIQUE (numero_conta, numero_item),

    CONSTRAINT ck_despesa_quantidade
        CHECK (quantidade > 0),

    CONSTRAINT ck_despesa_valor_apresentado
        CHECK (valor_apresentado >= 0),

    CONSTRAINT ck_despesa_valor_pago
        CHECK (valor_pago >= 0),

    CONSTRAINT ck_despesa_pagamento
        CHECK (
            (data_pagamento IS NULL AND id_tempo_pagamento IS NULL)
            OR
            (data_pagamento IS NOT NULL AND id_tempo_pagamento IS NOT NULL)
        )
);

-- ============================================================
-- ÍNDICES PARA CONSULTAS ANALÍTICAS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_receita_beneficiario
    ON fato_receita (id_beneficiario);

CREATE INDEX IF NOT EXISTS idx_receita_contrato
    ON fato_receita (id_contrato);

CREATE INDEX IF NOT EXISTS idx_receita_competencia
    ON fato_receita (id_tempo_competencia);

CREATE INDEX IF NOT EXISTS idx_despesa_beneficiario
    ON fato_despesa_assistencial (id_beneficiario);

CREATE INDEX IF NOT EXISTS idx_despesa_prestador
    ON fato_despesa_assistencial (id_prestador);

CREATE INDEX IF NOT EXISTS idx_despesa_procedimento
    ON fato_despesa_assistencial (id_procedimento);

CREATE INDEX IF NOT EXISTS idx_despesa_atendimento
    ON fato_despesa_assistencial (id_tempo_atendimento);

CREATE INDEX IF NOT EXISTS idx_despesa_pagamento
    ON fato_despesa_assistencial (id_tempo_pagamento);

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================
