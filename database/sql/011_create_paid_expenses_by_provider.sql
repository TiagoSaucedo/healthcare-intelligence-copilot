-- ============================================================
-- 011 - Despesas pagas por prestador e mês de pagamento
-- Healthcare Intelligence Copilot
-- ============================================================

CREATE OR REPLACE VIEW vw_despesa_paga_por_prestador AS

SELECT
    t.ano_mes,
    p.id_prestador,
    p.codigo_prestador,
    p.nome_prestador,
    p.tipo_prestador,
    p.especialidade,
    p.cidade,
    p.estado,

    COUNT(*) AS total_itens_pagos,

    COUNT(DISTINCT d.numero_conta)
        AS total_contas_pagas,

    COUNT(DISTINCT b.codigo_beneficiario)
        AS total_beneficiarios,

    ROUND(SUM(d.valor_pago), 2)
        AS despesa_paga

FROM fato_despesa_assistencial d

INNER JOIN dim_prestador p
    ON p.id_prestador = d.id_prestador

INNER JOIN dim_beneficiario b
    ON b.id_beneficiario = d.id_beneficiario

INNER JOIN dim_tempo t
    ON t.id_tempo = d.id_tempo_pagamento

WHERE
    d.data_pagamento IS NOT NULL

GROUP BY
    t.ano_mes,
    p.id_prestador,
    p.codigo_prestador,
    p.nome_prestador,
    p.tipo_prestador,
    p.especialidade,
    p.cidade,
    p.estado;
