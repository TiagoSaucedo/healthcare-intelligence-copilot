
-- ============================================================
-- 005 - Indicadores de despesas por coorte de beneficiário
-- Healthcare Intelligence Copilot
-- ============================================================

CREATE OR REPLACE VIEW vw_sinistralidade_mensal AS

WITH receita_beneficiario_mes AS (
    SELECT
        b.codigo_beneficiario,
        t.ano_mes,
        SUM(r.valor_receita) AS receita
    FROM fato_receita r
    INNER JOIN dim_beneficiario b
        ON b.id_beneficiario = r.id_beneficiario
    INNER JOIN dim_tempo t
        ON t.id_tempo = r.id_tempo_competencia
    GROUP BY
        b.codigo_beneficiario,
        t.ano_mes
),

despesa_beneficiario_mes AS (
    SELECT
        b.codigo_beneficiario,
        t.ano_mes,
        SUM(d.valor_apresentado) AS despesa_apresentada,
        SUM(d.valor_pago) AS despesa_paga
    FROM fato_despesa_assistencial d
    INNER JOIN dim_beneficiario b
        ON b.id_beneficiario = d.id_beneficiario
    INNER JOIN dim_tempo t
        ON t.id_tempo = d.id_tempo_atendimento
    GROUP BY
        b.codigo_beneficiario,
        t.ano_mes
),

consolidado_beneficiario_mes AS (
    SELECT
        COALESCE(r.codigo_beneficiario, d.codigo_beneficiario)
            AS codigo_beneficiario,

        COALESCE(r.ano_mes, d.ano_mes) AS ano_mes,

        r.receita,
        COALESCE(d.despesa_apresentada, 0)
            AS despesa_apresentada,

        COALESCE(d.despesa_paga, 0)
            AS despesa_paga

    FROM receita_beneficiario_mes r

    FULL OUTER JOIN despesa_beneficiario_mes d
        ON d.codigo_beneficiario = r.codigo_beneficiario
        AND d.ano_mes = r.ano_mes
)

SELECT
    ano_mes,

    ROUND(SUM(COALESCE(receita, 0)), 2)
        AS receita_total,

    ROUND(SUM(despesa_apresentada), 2)
        AS despesa_apresentada_total,

    ROUND(SUM(despesa_paga), 2)
        AS despesa_paga_total,

    ROUND(
        100.0 * SUM(despesa_apresentada)
        / NULLIF(SUM(receita), 0),
        2
    ) AS relacao_despesa_apresentada_pct,

    ROUND(
        100.0 * SUM(despesa_paga)
        / NULLIF(SUM(receita), 0),
        2
    ) AS relacao_despesa_paga_pct,

    COUNT(*) FILTER (
        WHERE receita IS NOT NULL
    ) AS beneficiarios_com_receita,

    COUNT(*) FILTER (
        WHERE receita IS NULL
        AND despesa_apresentada > 0
    ) AS beneficiarios_com_despesa_sem_receita

FROM consolidado_beneficiario_mes
GROUP BY ano_mes;
