-- ============================================================
-- 008 - Visão analítica de despesas por contrato
-- Healthcare Intelligence Copilot
-- ============================================================

CREATE OR REPLACE VIEW vw_despesa_por_contrato AS

SELECT
    t.ano_mes,
    c.id_contrato,
    c.codigo_contrato,
    c.modalidade,
    c.cobertura,
    c.acomodacao,
    c.tipo_contrato,

    COUNT(*) AS quantidade_itens,

    COUNT(DISTINCT d.numero_conta)
        AS quantidade_contas,

    COUNT(DISTINCT b.codigo_beneficiario)
        AS quantidade_beneficiarios,

    SUM(d.quantidade)
        AS quantidade_procedimentos,

    SUM(d.valor_apresentado)
        AS valor_total_apresentado,

    SUM(d.valor_pago)
        AS valor_total_pago,

    AVG(d.valor_apresentado)
        AS media_valor_por_item,

    SUM(d.valor_apresentado)
        / NULLIF(COUNT(DISTINCT d.numero_conta), 0)
        AS media_valor_por_conta

FROM fato_despesa_assistencial d

INNER JOIN dim_contrato c
    ON c.id_contrato = d.id_contrato

INNER JOIN dim_beneficiario b
    ON b.id_beneficiario = d.id_beneficiario

INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_atendimento

GROUP BY
    t.ano_mes,
    c.id_contrato,
    c.codigo_contrato,
    c.modalidade,
    c.cobertura,
    c.acomodacao,
    c.tipo_contrato;