
-- ============================================================
-- 004 - Visão consolidada mensal
-- Healthcare Intelligence Copilot
-- ============================================================

CREATE OR REPLACE VIEW vw_visao_financeira_mensal AS

SELECT
    COALESCE(r.ano_mes, a.ano_mes, p.ano_mes) AS ano_mes,

    COALESCE(r.receita_total, 0) AS receita_competencia,

    COALESCE(a.despesa_apresentada, 0)
        AS despesa_apresentada_atendimento,

    COALESCE(p.despesa_paga, 0)
        AS despesa_paga_pagamento,

    ROUND(
        100.0 * a.despesa_apresentada
        / NULLIF(r.receita_total, 0),
        2
    ) AS relacao_apresentada_receita_pct,

    ROUND(
        100.0 * p.despesa_paga
        / NULLIF(r.receita_total, 0),
        2
    ) AS relacao_paga_receita_pct

FROM vw_receita_mensal_competencia r

FULL OUTER JOIN vw_despesa_mensal_atendimento a
    ON a.ano_mes = r.ano_mes

FULL OUTER JOIN vw_despesa_mensal_pagamento p
    ON p.ano_mes = COALESCE(r.ano_mes, a.ano_mes);
