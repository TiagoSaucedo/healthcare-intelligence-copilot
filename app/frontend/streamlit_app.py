import re

import altair as alt
import pandas as pd
import streamlit as st

from app.frontend.api_client import (
    APIClientError,
    HealthcareAPIClient,
)


def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_percentage(value: float) -> str:
    return f"{value:.2f}".replace(".", ",") + "%"


def create_brl_line_chart(dataframe: pd.DataFrame) -> alt.Chart:
    chart_df = (
        dataframe.rename_axis("ano_mes")
        .reset_index()
        .melt(
            id_vars="ano_mes",
            var_name="Indicador",
            value_name="Valor",
        )
    )

    chart_df["Valor formatado"] = chart_df["Valor"].map(format_brl)

    return (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "ano_mes:N",
                sort=None,
                title=None,
                axis=alt.Axis(labelAngle=-90),
            ),
            y=alt.Y(
                "Valor:Q",
                title=None,
                axis=alt.Axis(
                    labelExpr="replace(format(datum.value, ',.0f'), /,/g, '.')"
                ),
            ),
            color=alt.Color(
                "Indicador:N",
                scale=alt.Scale(
                    domain=[
                        "Despesa apresentada",
                        "Despesa paga",
                    ],
                    range=["#7FC4F2", "#0080FF"],
                ),
                legend=alt.Legend(title=None),
            ),
            tooltip=[
                alt.Tooltip("ano_mes:N", title="Mês"),
                alt.Tooltip("Indicador:N", title="Indicador"),
                alt.Tooltip("Valor formatado:N", title="Valor"),
            ],
        )
        .properties(height=350)
    )


st.set_page_config(
    page_title="Healthcare Intelligence Copilot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Healthcare Intelligence Copilot")

st.markdown(
    """
    Plataforma de inteligência analítica em saúde,
    com indicadores financeiros, análises assistenciais
    e interação com um assistente de IA.
    """
)


@st.cache_resource
def get_api_client():
    return HealthcareAPIClient()


api_client = get_api_client()


try:
    health = api_client.get_health()
    st.success("API conectada e operacional.")

except APIClientError as exc:
    st.error(f"Não foi possível conectar à API: {exc}")
    st.stop()


st.sidebar.header("Filtros")

start_month = st.sidebar.text_input(
    "Mês inicial",
    value="2028-01",
    max_chars=7,
)

end_month = st.sidebar.text_input(
    "Mês final",
    value="2028-12",
    max_chars=7,
)


def is_valid_month(value: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value))


if not is_valid_month(start_month) or not is_valid_month(end_month):
    st.sidebar.error("Informe os meses no formato AAAA-MM.")
    st.stop()

if start_month > end_month:
    st.sidebar.error("O mês inicial não pode ser posterior ao mês final.")
    st.stop()


try:
    financial_summary = api_client.get_financial_summary(
        start_month,
        end_month,
    )

except APIClientError as exc:
    st.error(f"Erro ao carregar indicadores financeiros: {exc}")
    st.stop()


try:
    financial_monthly = api_client.get_financial_monthly(
        start_month,
        end_month,
    )

except APIClientError as exc:
    st.error(f"Erro ao carregar a evolução financeira: {exc}")
    st.stop()

try:
    provider_summary = api_client.get_provider_summary(
        start_month,
        end_month,
    )

    paid_provider_summary = api_client.get_paid_provider_summary(
        start_month,
        end_month,
    )

    procedure_summary = api_client.get_procedure_summary(
        start_month,
        end_month,
    )

    procedure_monthly = api_client.get_procedure_monthly(
        start_month,
        end_month,
    )

    contract_summary = api_client.get_contract_summary(
        start_month,
        end_month,
    )

    contract_monthly = api_client.get_contract_monthly(
        start_month,
        end_month,
    )

    provider_monthly = api_client.get_provider_monthly(
        start_month,
        end_month,
    )

    paid_provider_monthly = api_client.get_paid_provider_monthly(
        start_month,
        end_month,
    )

except APIClientError as exc:
    st.error(f"Erro ao carregar os indicadores de prestadores: {exc}")
    st.stop()

# Visão Financeira
st.header("Visão Financeira")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Receita total",
    format_brl(financial_summary["receita_total"]),
)

col2.metric(
    "Despesa apresentada",
    format_brl(financial_summary["despesa_apresentada_total"]),
)

col3.metric(
    "Despesa paga",
    format_brl(financial_summary["despesa_paga_total"]),
)

col4, col5 = st.columns(2)

col4.metric(
    "Relação despesa apresentada / receita",
    format_percentage(financial_summary["relacao_apresentada_receita_pct"]),
)

col5.metric(
    "Relação despesa paga / receita",
    format_percentage(financial_summary["relacao_paga_receita_pct"]),
)


st.subheader("Evolução financeira mensal")

financial_df = pd.DataFrame(financial_monthly)

financial_df = financial_df.set_index("ano_mes")

financial_df = financial_df.rename(
    columns={
        "receita_competencia": "Receita por competência",
        "despesa_apresentada_atendimento": "Despesa apresentada",
        "despesa_paga_pagamento": "Despesa paga",
    }
)

financial_chart_df = (
    financial_df.reset_index()
    .melt(
        id_vars="ano_mes",
        var_name="Indicador",
        value_name="Valor",
    )
)

financial_chart_df["Valor formatado"] = (
    financial_chart_df["Valor"].map(format_brl)
)

financial_chart = (
    alt.Chart(financial_chart_df)
    .mark_line(point=True)
    .encode(
        x=alt.X(
            "ano_mes:N",
            sort=None,
            title=None,
            axis=alt.Axis(labelAngle=-90),
        ),
        y=alt.Y(
            "Valor:Q",
            title=None,
            axis=alt.Axis(
                labelExpr="replace(format(datum.value, ',.0f'), /,/g, '.')"
            ),
        ),
        color=alt.Color(
            "Indicador:N",
            scale=alt.Scale(
                domain=[
                    "Despesa apresentada",
                    "Despesa paga",
                    "Receita por competência",
                ],
                range=["#7FC4F2", "#0080FF", "#FFB6C1"],
            ),
            legend=alt.Legend(title=None),
        ),
        tooltip=[
            alt.Tooltip("ano_mes:N", title="Mês"),
            alt.Tooltip("Indicador:N", title="Indicador"),
            alt.Tooltip(
                "Valor formatado:N",
                title="Valor",
            ),
        ],
    )
    .properties(
        height=350,
    )
)

st.altair_chart(
    financial_chart,
    use_container_width=True,
)

st.divider()

# Analise de Prestadores
st.header("Análise de Prestadores")

st.subheader("Visão geral")

provider_col1, provider_col2, provider_col3 = st.columns(3)

provider_col1.metric(
    "Prestadores",
    format_number(provider_summary["quantidade_prestadores"]),
)

provider_col2.metric(
    "Itens analisados",
    format_number(provider_summary["quantidade_itens"]),
)

provider_col3.metric(
    "Contas analisadas",
    format_number(provider_summary["quantidade_contas"]),
)

provider_col4, provider_col5 = st.columns(2)

provider_col4.metric(
    "Despesa apresentada",
    format_brl(provider_summary["despesa_apresentada_total"]),
)

provider_col5.metric(
    "Despesa paga",
    format_brl(paid_provider_summary["despesa_paga_total"]),
)

st.subheader("Evolução mensal das despesas")

provider_monthly_df = pd.DataFrame(provider_monthly)

paid_provider_monthly_df = pd.DataFrame(paid_provider_monthly)

presented_monthly = (
    provider_monthly_df
    .groupby("ano_mes")["despesa_apresentada"]
    .sum()
)

paid_monthly = (
    paid_provider_monthly_df
    .groupby("ano_mes")["despesa_paga"]
    .sum()
)

provider_expenses_df = pd.concat(
    [
        presented_monthly.rename("Despesa apresentada"),
        paid_monthly.rename("Despesa paga"),
    ],
    axis=1,
).fillna(0)

st.altair_chart(
    create_brl_line_chart(provider_expenses_df),
    use_container_width=True,
)

st.divider()

# Análise de Procedimentos
st.header("Análise de Procedimentos")

st.subheader("Visão geral")

procedure_col1, procedure_col2, procedure_col3 = st.columns(3)

procedure_col1.metric(
    "Procedimentos",
    format_number(procedure_summary["quantidade_procedimentos"]),
)

procedure_col2.metric(
    "Itens analisados",
    format_number(procedure_summary["quantidade_itens"]),
)

procedure_col3.metric(
    "Contas analisadas",
    format_number(procedure_summary["quantidade_contas"]),
)

procedure_col4, procedure_col5 = st.columns(2)

procedure_col4.metric(
    "Despesa apresentada",
    format_brl(procedure_summary["despesa_apresentada_total"]),
)

procedure_col5.metric(
    "Despesa paga",
    format_brl(procedure_summary["despesa_paga_total"]),
)

st.subheader("Evolução mensal das despesas por procedimento")

procedure_monthly_df = pd.DataFrame(procedure_monthly)

procedure_expenses_df = (
    procedure_monthly_df
    .groupby("ano_mes")[
        ["despesa_apresentada", "despesa_paga"]
    ]
    .sum()
    .rename(
        columns={
            "despesa_apresentada": "Despesa apresentada",
            "despesa_paga": "Despesa paga",
        }
    )
)

st.altair_chart(
    create_brl_line_chart(procedure_expenses_df),
    use_container_width=True,
)

st.divider()

# Análise de Contratos
st.header("Análise de Contratos")

st.subheader("Visão geral")

contract_col1, contract_col2, contract_col3 = st.columns(3)

contract_col1.metric(
    "Contratos",
    format_number(contract_summary["quantidade_contratos"]),
)

contract_col2.metric(
    "Itens analisados",
    format_number(contract_summary["quantidade_itens"]),
)

contract_col3.metric(
    "Contas analisadas",
    format_number(contract_summary["quantidade_contas"]),
)

contract_col4, contract_col5 = st.columns(2)

contract_col4.metric(
    "Despesa apresentada",
    format_brl(contract_summary["despesa_apresentada_total"]),
)

contract_col5.metric(
    "Despesa paga",
    format_brl(contract_summary["despesa_paga_total"]),
)

contract_col6, contract_col7 = st.columns(2)

contract_col6.metric(
    "Valor médio por item",
    format_brl(contract_summary["valor_medio_por_item"]),
)

contract_col7.metric(
    "Valor médio por conta",
    format_brl(contract_summary["valor_medio_por_conta"]),
)

st.subheader("Evolução mensal das despesas por contrato")

contract_monthly_df = pd.DataFrame(contract_monthly)

contract_expenses_df = (
    contract_monthly_df
    .groupby("ano_mes")[
        ["valor_total_apresentado", "valor_total_pago"]
    ]
    .sum()
    .rename(
        columns={
            "valor_total_apresentado": "Despesa apresentada",
            "valor_total_pago": "Despesa paga",
        }
    )
)

st.altair_chart(
    create_brl_line_chart(contract_expenses_df),
    use_container_width=True,
)

st.divider()

st.header("Rankings Analíticos")

st.subheader("Filtros do ranking")

ranking_col1, ranking_col2, ranking_col3 = st.columns(3)

with ranking_col1:
    ranking_dimension_label = st.selectbox(
        "Dimensão",
        ["Prestadores", "Procedimentos", "Contratos"],
    )

with ranking_col2:
    ranking_metric_label = st.selectbox(
        "Métrica",
        ["Despesa apresentada", "Despesa paga"],
    )

with ranking_col3:
    ranking_limit = st.selectbox(
        "Quantidade de posições",
        [5, 10, 15, 20],
        index=1,
    )

ranking_dimensions = {
    "Prestadores": "prestador",
    "Procedimentos": "procedimento",
    "Contratos": "contrato",
}

ranking_metrics = {
    "Despesa apresentada": "apresentada",
    "Despesa paga": "paga",
}

ranking_dimension = ranking_dimensions[ranking_dimension_label]
ranking_metric = ranking_metrics[ranking_metric_label]

try:
    ranking_summary = api_client.get_ranking_summary(
        ranking_dimension,
        start_month,
        end_month,
        ranking_metric,
    )

    ranking_data = api_client.get_ranking(
        ranking_dimension,
        start_month,
        end_month,
        ranking_limit,
        ranking_metric,
    )

    ranking_analysis = api_client.get_ranking_analysis(
        ranking_dimension,
        start_month,
        end_month,
        ranking_limit,
        ranking_metric,
    )

except APIClientError as exc:
    st.error(f"Erro ao carregar o ranking: {exc}")
    st.stop()

# Resumo do ranking
st.subheader("Resumo do ranking")

ranking_metric_col1, ranking_metric_col2, ranking_metric_col3 = (
    st.columns(3)
)

ranking_metric_col1.metric(
    "Entidades analisadas",
    format_number(ranking_summary["quantidade_entidades"]),
)

ranking_metric_col2.metric(
    "Itens analisados",
    format_number(ranking_summary["quantidade_itens"]),
)

ranking_metric_col3.metric(
    "Despesa total",
    format_brl(ranking_summary["valor_total"]),
)

# Concentração do ranking
st.subheader("Concentração do ranking")

analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

analysis_col1.metric(
    "Entidades no Top N",
    format_number(ranking_analysis["quantidade_entidades_retornadas"]),
)

analysis_col2.metric(
    "Despesa do Top N",
    format_brl(ranking_analysis["valor_total_top_n"]),
)

analysis_col3.metric(
    "Participação conjunta",
    format_percentage(ranking_analysis["participacao_conjunta_pct"]),
)
# Classificação
st.subheader("Classificação")

if ranking_data:
    ranking_df = pd.DataFrame(ranking_data)

    ranking_df = ranking_df.rename(
        columns={
            "ranking": "Posição",
            "nome_entidade": "Entidade",
            "quantidade_itens": "Itens",
            "quantidade_contas": "Contas",
            "valor_despesa": "Despesa",
            "participacao_pct": "Participação (%)",
        }
    )

    ranking_df = ranking_df[
        [
            "Posição",
            "Entidade",
            "Itens",
            "Contas",
            "Despesa",
            "Participação (%)",
        ]
    ]

    ranking_df["Despesa"] = ranking_df["Despesa"].map(format_brl)

    ranking_df["Participação (%)"] = (
        ranking_df["Participação (%)"].map(format_percentage)
    )

    st.dataframe(
        ranking_df,
        width="stretch",
        hide_index=True,
    )

else:
    st.info("Nenhum resultado encontrado para os filtros selecionados.")

st.divider()

st.header("Assistente de Inteligência em Saúde")

st.caption(
    "Faça perguntas em linguagem natural sobre os dados "
    "financeiros e assistenciais disponíveis no sistema."
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Digite sua pergunta sobre os dados..."):
    st.session_state.chat_messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.spinner(
        "Analisando os dados..."
    ):
        try:
            chat_response = api_client.post_chat(prompt)
            answer = chat_response["answer"]

        except (APIClientError, KeyError) as exc:
            answer = f"Não foi possível obter uma resposta: {exc}"

        st.markdown(answer)

    st.session_state.chat_messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
