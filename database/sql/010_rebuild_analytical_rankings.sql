
-- ============================================================
-- 010 - Reestruturação das bases de rankings analíticos
-- Preserva a granularidade mensal por entidade.
-- Ranking e participação percentual serão calculados
-- dinamicamente na camada de aplicação.
-- ============================================================


-- 1. Base mensal de despesas por prestador
CREATE OR REPLACE VIEW vw_ranking_despesa_prestador AS
SELECT
    ano_mes,
    id_prestador,
    codigo_prestador,
    nome_prestador,
    tipo_prestador,
    especialidade,
    cidade,
    estado,
    SUM(total_itens) AS quantidade_itens,
    SUM(total_contas) AS quantidade_contas,
    SUM(total_beneficiarios) AS quantidade_beneficiarios,
    SUM(despesa_apresentada) AS despesa_apresentada,
    SUM(despesa_paga) AS despesa_paga
FROM vw_despesa_por_prestador
GROUP BY
    ano_mes,
    id_prestador,
    codigo_prestador,
    nome_prestador,
    tipo_prestador,
    especialidade,
    cidade,
    estado;


-- 2. Base mensal de despesas por procedimento
CREATE OR REPLACE VIEW vw_ranking_despesa_procedimento AS
SELECT
    ano_mes,
    id_procedimento,
    codigo_procedimento,
    descricao,
    grupo_procedimento,
    categoria,
    tipo_procedimento,
    SUM(total_itens) AS quantidade_itens,
    SUM(total_contas) AS quantidade_contas,
    SUM(total_beneficiarios) AS quantidade_beneficiarios,
    SUM(quantidade_total) AS quantidade_total,
    SUM(despesa_apresentada) AS despesa_apresentada,
    SUM(despesa_paga) AS despesa_paga
FROM vw_despesa_por_procedimento
GROUP BY
    ano_mes,
    id_procedimento,
    codigo_procedimento,
    descricao,
    grupo_procedimento,
    categoria,
    tipo_procedimento;


-- 3. Base mensal de despesas por contrato
CREATE OR REPLACE VIEW vw_ranking_despesa_contrato AS
SELECT
    ano_mes,
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
    ano_mes,
    id_contrato,
    codigo_contrato,
    modalidade,
    cobertura,
    acomodacao,
    tipo_contrato;
