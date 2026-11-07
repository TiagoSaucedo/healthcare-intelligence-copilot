
-- ============================================================
-- HEALTHCARE INTELLIGENCE COPILOT
-- 002 - Adequação da dimensão beneficiário para SCD Tipo 2
-- ============================================================

-- Permite múltiplas versões do mesmo beneficiário.
ALTER TABLE dim_beneficiario
DROP CONSTRAINT IF EXISTS dim_beneficiario_codigo_beneficiario_key;

-- Identifica a versão cadastral vigente.
ALTER TABLE dim_beneficiario
ADD COLUMN IF NOT EXISTS ativo_atual BOOLEAN NOT NULL DEFAULT TRUE;

-- Apenas uma versão atual por beneficiário.
CREATE UNIQUE INDEX IF NOT EXISTS
    uq_beneficiario_versao_atual
ON dim_beneficiario (codigo_beneficiario)
WHERE ativo_atual = TRUE;

-- Garante coerência entre vigência e situação atual.
ALTER TABLE dim_beneficiario
ADD CONSTRAINT ck_beneficiario_scd2_vigencia
CHECK (
    (ativo_atual = TRUE AND data_fim_vigencia IS NULL)
    OR
    (ativo_atual = FALSE AND data_fim_vigencia IS NOT NULL)
);
