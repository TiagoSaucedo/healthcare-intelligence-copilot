
import re

import pandas as pd
import streamlit as st

from app.frontend.api_client import (
    APIClientError,
    HealthcareAPIClient,
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

st.header("Visão Financeira")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Receita total",
    f"R$ {financial_summary['receita_total']:,.2f}",
)

col2.metric(
    "Despesa apresentada",
    f"R$ {financial_summary['despesa_apresentada_total']:,.2f}",
)

col3.metric(
    "Despesa paga",
    f"R$ {financial_summary['despesa_paga_total']:,.2f}",
)

col4, col5 = st.columns(2)

col4.metric(
    "Relação despesa apresentada / receita",
    f"{financial_summary['relacao_apresentada_receita_pct']:.2f}%",
)

col5.metric(
    "Relação despesa paga / receita",
    f"{financial_summary['relacao_paga_receita_pct']:.2f}%",
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

st.line_chart(
    financial_df[
        [
            "Receita por competência",
            "Despesa apresentada",
            "Despesa paga",
        ]
    ]
)

st.divider()

st.header("Análise de Prestadores")

st.subheader("Visão geral")

provider_col1, provider_col2, provider_col3 = st.columns(3)

provider_col1.metric(
    "Prestadores",
    f"{provider_summary['quantidade_prestadores']:,}",
)

provider_col2.metric(
    "Itens analisados",
    f"{provider_summary['quantidade_itens']:,}",
)

provider_col3.metric(
    "Contas analisadas",
    f"{provider_summary['quantidade_contas']:,}",
)

provider_col4, provider_col5 = st.columns(2)

provider_col4.metric(
    "Despesa apresentada",
    f"R$ {provider_summary['despesa_apresentada_total']:,.2f}",
)

provider_col5.metric(
    "Despesa paga",
    f"R$ {paid_provider_summary['despesa_paga_total']:,.2f}",
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

st.line_chart(provider_expenses_df)

st.divider()

st.header("Análise de Procedimentos")

st.subheader("Visão geral")

procedure_col1, procedure_col2, procedure_col3 = st.columns(3)

procedure_col1.metric(
    "Procedimentos",
    f"{procedure_summary['quantidade_procedimentos']:,}",
)

procedure_col2.metric(
    "Itens analisados",
    f"{procedure_summary['quantidade_itens']:,}",
)

procedure_col3.metric(
    "Contas analisadas",
    f"{procedure_summary['quantidade_contas']:,}",
)

procedure_col4, procedure_col5 = st.columns(2)

procedure_col4.metric(
    "Despesa apresentada",
    f"R$ {procedure_summary['despesa_apresentada_total']:,.2f}",
)

procedure_col5.metric(
    "Despesa paga",
    f"R$ {procedure_summary['despesa_paga_total']:,.2f}",
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

st.line_chart(procedure_expenses_df)

st.divider()

st.header("Análise de Contratos")

st.subheader("Visão geral")

contract_col1, contract_col2, contract_col3 = st.columns(3)

contract_col1.metric(
    "Contratos",
    f"{contract_summary['quantidade_contratos']:,}",
)

contract_col2.metric(
    "Itens analisados",
    f"{contract_summary['quantidade_itens']:,}",
)

contract_col3.metric(
    "Contas analisadas",
    f"{contract_summary['quantidade_contas']:,}",
)

contract_col4, contract_col5 = st.columns(2)

contract_col4.metric(
    "Despesa apresentada",
    f"R$ {contract_summary['despesa_apresentada_total']:,.2f}",
)

contract_col5.metric(
    "Despesa paga",
    f"R$ {contract_summary['despesa_paga_total']:,.2f}",
)

contract_col6, contract_col7 = st.columns(2)

contract_col6.metric(
    "Valor médio por item",
    f"R$ {contract_summary['valor_medio_por_item']:,.2f}",
)

contract_col7.metric(
    "Valor médio por conta",
    f"R$ {contract_summary['valor_medio_por_conta']:,.2f}",
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

st.line_chart(contract_expenses_df)

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

st.subheader("Resumo do ranking")

ranking_metric_col1, ranking_metric_col2, ranking_metric_col3 = (
    st.columns(3)
)

ranking_metric_col1.metric(
    "Entidades analisadas",
    f"{ranking_summary['quantidade_entidades']:,}",
)

ranking_metric_col2.metric(
    "Itens analisados",
    f"{ranking_summary['quantidade_itens']:,}",
)

ranking_metric_col3.metric(
    "Despesa total",
    f"R$ {ranking_summary['valor_total']:,.2f}",
)

st.subheader("Concentração do ranking")

analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

analysis_col1.metric(
    "Entidades no Top N",
    f"{ranking_analysis['quantidade_entidades_retornadas']:,}",
)

analysis_col2.metric(
    "Despesa do Top N",
    f"R$ {ranking_analysis['valor_total_top_n']:,.2f}",
)

analysis_col3.metric(
    "Participação conjunta",
    f"{ranking_analysis['participacao_conjunta_pct']:.2f}%",
)

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

    ranking_df["Despesa"] = ranking_df["Despesa"].map(
        lambda value: f"R$ {value:,.2f}"
    )

    ranking_df["Participação (%)"] = (
        ranking_df["Participação (%)"].map(
            lambda value: f"{value:.2f}%"
        )
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
