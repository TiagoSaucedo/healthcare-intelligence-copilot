-- ============================================================
-- 009 - Rankings analíticos de despesas assistenciais
-- ============================================================

-- 1. Ranking de prestadores
CREATE OR REPLACE VIEW vw_ranking_despesa_prestador AS
WITH despesas AS (
    SELECT
        id_prestador,
        codigo_prestador,
        nome_prestador,
        tipo_prestador,
        especialidade,
        cidade,
        estado,
        SUM(total_itens) AS quantidade_itens,
        SUM(total_contas) AS quantidade_contas,
        SUM(despesa_apresentada) AS despesa_apresentada,
        SUM(despesa_paga) AS despesa_paga
    FROM vw_despesa_por_prestador
    GROUP BY
        id_prestador,
        codigo_prestador,
        nome_prestador,
        tipo_prestador,
        especialidade,
        cidade,
        estado
),
total AS (
    SELECT SUM(despesa_apresentada) AS despesa_total
    FROM despesas
)
SELECT
    DENSE_RANK() OVER (
        ORDER BY d.despesa_apresentada DESC
    ) AS ranking,
    d.*,
    ROUND(
        100.0 * d.despesa_apresentada
        / NULLIF(t.despesa_total, 0),
        2
    ) AS participacao_pct
FROM despesas d
CROSS JOIN total t;


-- 2. Ranking de procedimentos
CREATE OR REPLACE VIEW vw_ranking_despesa_procedimento AS
WITH despesas AS (
    SELECT
        id_procedimento,
        codigo_procedimento,
        descricao,
        grupo_procedimento,
        categoria,
        tipo_procedimento,
        SUM(total_itens) AS quantidade_itens,
        SUM(total_contas) AS quantidade_contas,
        SUM(quantidade_total) AS quantidade_total,
        SUM(despesa_apresentada) AS despesa_apresentada,
        SUM(despesa_paga) AS despesa_paga
    FROM vw_despesa_por_procedimento
    GROUP BY
        id_procedimento,
        codigo_procedimento,
        descricao,
        grupo_procedimento,
        categoria,
        tipo_procedimento
),
total AS (
    SELECT SUM(despesa_apresentada) AS despesa_total
    FROM despesas
)
SELECT
    DENSE_RANK() OVER (
        ORDER BY d.despesa_apresentada DESC
    ) AS ranking,
    d.*,
    ROUND(
        100.0 * d.despesa_apresentada
        / NULLIF(t.despesa_total, 0),
        2
    ) AS participacao_pct
FROM despesas d
CROSS JOIN total t;


-- 3. Ranking de contratos
CREATE OR REPLACE VIEW vw_ranking_despesa_contrato AS
WITH despesas AS (
    SELECT
        id_contrato,
        codigo_contrato,
        modalidade,
        cobertura,
        acomodacao,
        tipo_contrato,
        SUM(quantidade_itens) AS quantidade_itens,
        SUM(quantidade_contas) AS quantidade_contas,
        SUM(quantidade_beneficiarios) AS quantidade_beneficiarios,
        SUM(quantidade_procedimentos) AS quantidade_procedimentos,
        SUM(valor_total_apresentado) AS despesa_apresentada,
        SUM(valor_total_pago) AS despesa_paga
    FROM vw_despesa_por_contrato
    GROUP BY
        id_contrato,
        codigo_contrato,
        modalidade,
        cobertura,
        acomodacao,
        tipo_contrato
),
total AS (
    SELECT SUM(despesa_apresentada) AS despesa_total
    FROM despesas
)
SELECT
    DENSE_RANK() OVER (
        ORDER BY d.despesa_apresentada DESC
    ) AS ranking,
    d.*,
    ROUND(
        100.0 * d.despesa_apresentada
        / NULLIF(t.despesa_total, 0),
        2
    ) AS participacao_pct
FROM despesas d
CROSS JOIN total t;