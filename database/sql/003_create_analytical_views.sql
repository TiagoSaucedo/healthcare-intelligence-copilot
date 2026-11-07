
-- ============================================================
-- 003 - Camada analítica mensal
-- Healthcare Intelligence Copilot
-- ============================================================

-- 1. Receita reconhecida por competência
CREATE OR REPLACE VIEW vw_receita_mensal_competencia AS
SELECT
    t.ano_mes,
    SUM(r.valor_receita) AS receita_total,
    COUNT(*) AS total_lancamentos,
    COUNT(DISTINCT r.id_beneficiario) AS total_beneficiarios
FROM fato_receita r
INNER JOIN dim_tempo t
    ON t.id_tempo = r.id_tempo_competencia
GROUP BY
    t.ano_mes;


-- 2. Despesa apresentada por mês de atendimento
CREATE OR REPLACE VIEW vw_despesa_mensal_atendimento AS
SELECT
    t.ano_mes,
    SUM(d.valor_apresentado) AS despesa_apresentada,
    COUNT(*) AS total_itens,
    COUNT(DISTINCT d.numero_conta) AS total_contas
FROM fato_despesa_assistencial d
INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_atendimento
GROUP BY
    t.ano_mes;


-- 3. Despesa paga por mês de pagamento
-- Itens pendentes não entram nesta visão.
CREATE OR REPLACE VIEW vw_despesa_mensal_pagamento AS
SELECT
    t.ano_mes,
    SUM(d.valor_pago) AS despesa_paga,
    COUNT(*) AS total_itens_pagos,
    COUNT(DISTINCT d.numero_conta) AS total_contas_pagas
FROM fato_despesa_assistencial d
INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_pagamento
WHERE
    d.data_pagamento IS NOT NULL
GROUP BY
    t.ano_mes;
