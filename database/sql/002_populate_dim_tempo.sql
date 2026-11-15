-- Healthcare Intelligence Copilot
-- Populate date dimension (2024-2028)

INSERT INTO dim_tempo (
    id_tempo,
    data,
    ano,
    trimestre,
    mes,
    nome_mes,
    ano_mes
)
SELECT
    TO_CHAR(dia, 'YYYYMMDD')::INTEGER,
    dia::DATE,
    EXTRACT(YEAR FROM dia)::SMALLINT,
    EXTRACT(QUARTER FROM dia)::SMALLINT,
    EXTRACT(MONTH FROM dia)::SMALLINT,
    TO_CHAR(dia, 'TMMonth'),
    TO_CHAR(dia, 'YYYY-MM')
FROM GENERATE_SERIES(
    DATE '2024-01-01',
    DATE '2028-12-31',
    INTERVAL '1 day'
) AS dia
ON CONFLICT (data) DO NOTHING;