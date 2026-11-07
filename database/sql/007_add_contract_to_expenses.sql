
-- ============================================================
-- 007 - Inclusão do contrato na fato de despesas
-- Healthcare Intelligence Copilot
-- ============================================================

BEGIN;

-- 1. Adicionar a chave do contrato
ALTER TABLE fato_despesa_assistencial
ADD COLUMN id_contrato BIGINT;

-- 2. Recuperar o contrato associado ao beneficiário
-- Cada beneficiário possui um único contrato no histórico
-- sintético atual.

UPDATE fato_despesa_assistencial d
SET id_contrato = m.id_contrato
FROM dim_beneficiario b,
(
    SELECT
        db.codigo_beneficiario,
        MIN(r.id_contrato) AS id_contrato
    FROM fato_receita r
    INNER JOIN dim_beneficiario db
        ON db.id_beneficiario = r.id_beneficiario
    GROUP BY
        db.codigo_beneficiario
    HAVING COUNT(DISTINCT r.id_contrato) = 1
) m
WHERE
    b.id_beneficiario = d.id_beneficiario
    AND b.codigo_beneficiario = m.codigo_beneficiario;

-- 3. Impedir a migração se houver despesas sem contrato
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM fato_despesa_assistencial
        WHERE id_contrato IS NULL
    ) THEN
        RAISE EXCEPTION
            'Existem despesas sem contrato associado. Migração cancelada.';
    END IF;
END $$;

-- 4. Criar relacionamento com a dimensão de contratos
ALTER TABLE fato_despesa_assistencial
ADD CONSTRAINT fk_despesa_contrato
FOREIGN KEY (id_contrato)
REFERENCES dim_contrato (id_contrato);

-- 5. Tornar a chave obrigatória
ALTER TABLE fato_despesa_assistencial
ALTER COLUMN id_contrato SET NOT NULL;

-- 6. Criar índice para consultas analíticas
CREATE INDEX idx_despesa_contrato
ON fato_despesa_assistencial (id_contrato);

COMMIT;
