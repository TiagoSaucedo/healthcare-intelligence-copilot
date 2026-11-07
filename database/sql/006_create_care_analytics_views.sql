
-- ============================================================
-- 006 - Análises assistenciais por prestador e procedimento
-- Healthcare Intelligence Copilot
-- ============================================================


-- 1. Despesas por prestador e mês de atendimento

CREATE OR REPLACE VIEW vw_despesa_por_prestador AS

SELECT
    t.ano_mes,
    p.id_prestador,
    p.codigo_prestador,
    p.nome_prestador,
    p.tipo_prestador,
    p.especialidade,
    p.cidade,
    p.estado,

    COUNT(*) AS total_itens,

    COUNT(DISTINCT d.numero_conta)
        AS total_contas,

    COUNT(DISTINCT b.codigo_beneficiario)
        AS total_beneficiarios,

    ROUND(SUM(d.valor_apresentado), 2)
        AS despesa_apresentada,

    ROUND(SUM(d.valor_pago), 2)
        AS despesa_paga,

    ROUND(AVG(d.valor_apresentado), 2)
        AS valor_medio_por_item,

    ROUND(
        SUM(d.valor_apresentado)
        / NULLIF(COUNT(DISTINCT d.numero_conta), 0),
        2
    ) AS valor_medio_por_conta

FROM fato_despesa_assistencial d

INNER JOIN dim_prestador p
    ON p.id_prestador = d.id_prestador

INNER JOIN dim_beneficiario b
    ON b.id_beneficiario = d.id_beneficiario

INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_atendimento

GROUP BY
    t.ano_mes,
    p.id_prestador,
    p.codigo_prestador,
    p.nome_prestador,
    p.tipo_prestador,
    p.especialidade,
    p.cidade,
    p.estado;


-- 2. Despesas por procedimento e mês de atendimento

CREATE OR REPLACE VIEW vw_despesa_por_procedimento AS

SELECT
    t.ano_mes,
    pr.id_procedimento,
    pr.codigo_procedimento,
    pr.descricao,
    pr.grupo_procedimento,
    pr.categoria,
    pr.tipo_procedimento,

    COUNT(*) AS total_itens,

    COUNT(DISTINCT d.numero_conta)
        AS total_contas,

    COUNT(DISTINCT b.codigo_beneficiario)
        AS total_beneficiarios,

    SUM(d.quantidade) AS quantidade_total,

    ROUND(SUM(d.valor_apresentado), 2)
        AS despesa_apresentada,

    ROUND(SUM(d.valor_pago), 2)
        AS despesa_paga,

    ROUND(AVG(d.valor_apresentado), 2)
        AS valor_medio_por_item,

    ROUND(
        SUM(d.valor_apresentado)
        / NULLIF(SUM(d.quantidade), 0),
        2
    ) AS valor_medio_por_unidade

FROM fato_despesa_assistencial d

INNER JOIN dim_procedimento pr
    ON pr.id_procedimento = d.id_procedimento

INNER JOIN dim_beneficiario b
    ON b.id_beneficiario = d.id_beneficiario

INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_atendimento

GROUP BY
    t.ano_mes,
    pr.id_procedimento,
    pr.codigo_procedimento,
    pr.descricao,
    pr.grupo_procedimento,
    pr.categoria,
    pr.tipo_procedimento;
