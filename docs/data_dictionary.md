# Healthcare Intelligence Copilot
## Dicionário de Dados — Modelo Dimensional

**Versão:** 1.0  
**Banco de dados:** PostgreSQL 17 + pgvector  
**Contexto:** Operadora de saúde — dados sintéticos

---

## 1. Objetivo

Definir o modelo dimensional responsável pelo armazenamento e pela análise de receitas e despesas assistenciais, permitindo calcular indicadores de desempenho, especialmente a sinistralidade.

O modelo será utilizado como fonte de verdade para as ferramentas analíticas e para os agentes inteligentes da aplicação.

## 2. Arquitetura dimensional

Modelo composto por duas tabelas fato e cinco dimensões compartilhadas.

### Tabelas fato

| Tabela | Descrição |
|---|---|
| fato_receita | Registros financeiros de receitas reconhecidas |
| fato_despesa_assistencial | Registros de despesas assistenciais por item |

### Tabelas dimensão

| Tabela | Descrição |
|---|---|
| dim_beneficiario | Cadastro e características dos beneficiários |
| dim_prestador | Hospitais, clínicas e demais prestadores |
| dim_procedimento | Procedimentos e classificações assistenciais |
| dim_tempo | Calendário e competências |
| dim_contrato | Contratos e modalidades de relacionamento |

## 3. Definição das tabelas fato

### 3.1 fato_receita

**Objetivo:** armazenar os valores de receita reconhecidos pela operadora.

**Grão:** um registro por lançamento de receita, beneficiário, contrato e competência.

| Campo | Tipo | Descrição |
|---|---|---|
| id_receita | BIGINT | Chave primária |
| id_beneficiario | BIGINT | Chave estrangeira |
| id_contrato | BIGINT | Chave estrangeira |
| id_tempo | INTEGER | Chave estrangeira |
| numero_lancamento | VARCHAR(50) | Identificação do lançamento |
| valor_receita | NUMERIC(15,2) | Valor reconhecido |
| data_reconhecimento | DATE | Data do reconhecimento |

**Regra de negócio:** a receita será considerada conforme o valor reconhecido na competência correspondente, evitando duplicidades na consolidação financeira.

### 3.2 fato_despesa_assistencial

**Objetivo:** armazenar os itens de despesas assistenciais realizados pelos beneficiários.

**Grão:** um registro por item de despesa assistencial.

| Campo | Tipo | Descrição |
|---|---|---|
| id_despesa | BIGINT | Chave primária |
| id_beneficiario | BIGINT | Chave estrangeira |
| id_prestador | BIGINT | Chave estrangeira |
| id_procedimento | BIGINT | Chave estrangeira |
| Campo	Descrição
id_tempo_atendimento | INTEGER | FK para o mês do atendimento |
id_tempo_pagamento | INTEGER | FK para o mês do pagamento; aceita nulo enquanto não houver pagamento |
| numero_conta | VARCHAR(50) | Identificação da conta assistencial |
| numero_item | INTEGER | Identificação do item |
| quantidade | NUMERIC(12,2) | Quantidade utilizada |
| valor_apresentado | NUMERIC(15,2) | Valor apresentado pelo prestador |
| valor_pago | NUMERIC(15,2) | Valor efetivamente pago |
| data_atendimento | DATE | Data do atendimento |
| data_pagamento | DATE | Data do pagamento |

**Regra de negócio:** o valor apresentado não deve ser confundido com o valor pago. Ambos serão preservados para análises financeiras e assistenciais.

## 4. Definição das dimensões

### 4.1 dim_beneficiario

| Campo | Tipo | Descrição |
|---|---|---|
| id_beneficiario | BIGINT | Chave substituta |
| codigo_beneficiario | VARCHAR(50) | Identificador sintético |
| faixa_etaria | VARCHAR(20) | Faixa etária |
| sexo | VARCHAR(20) | Categoria sintética |
| municipio | VARCHAR(100) | Município |
| uf | CHAR(2) | Estado |
| tipo_beneficiario | VARCHAR(30) | Titular ou dependente |
| data_inicio_vigencia | DATE | Início do vínculo |
| data_fim_vigencia | DATE | Fim do vínculo, quando aplicável |

### 4.2 dim_prestador

| Campo | Tipo | Descrição |
|---|---|---|
| id_prestador | BIGINT | Chave substituta |
| codigo_prestador | VARCHAR(50) | Identificador sintético |
| nome_prestador | VARCHAR(150) | Nome fictício |
| tipo_prestador | VARCHAR(50) | Hospital, clínica, laboratório etc. |
| municipio | VARCHAR(100) | Município |
| uf | CHAR(2) | Estado |
| especialidade_principal | VARCHAR(100) | Especialidade |

### 4.3 dim_procedimento

| Campo | Tipo | Descrição |
|---|---|---|
| id_procedimento | BIGINT | Chave substituta |
| codigo_procedimento | VARCHAR(50) | Código sintético |
| descricao | VARCHAR(200) | Descrição |
| grupo_procedimento | VARCHAR(100) | Grupo assistencial |
| categoria | VARCHAR(100) | Categoria |
| tipo | VARCHAR(50) | Consulta, exame, internação etc. |

### 4.4 dim_tempo

| Campo | Tipo | Descrição |
|---|---|---|
| id_tempo | INTEGER | Chave substituta |
| data | DATE | Data de referência |
| ano | SMALLINT | Ano |
| trimestre | SMALLINT | Trimestre |
| mes | SMALLINT | Mês |
| nome_mes | VARCHAR(20) | Nome do mês |
| ano_mes | CHAR(7) | Competência YYYY-MM |

A dimensão permitirá análises mensais, trimestrais e anuais.

### 4.5 dim_contrato

| Campo | Tipo | Descrição |
|---|---|---|
| id_contrato | BIGINT | Chave substituta |
| codigo_contrato | VARCHAR(50) | Identificador sintético |
| modalidade | VARCHAR(50) | Individual, coletivo empresarial etc. |
| abrangencia | VARCHAR(50) | Abrangência contratual |
| acomodacao | VARCHAR(50) | Tipo de acomodação |
| tipo_contratacao | VARCHAR(50) | Classificação contratual |

## 5. Regras de cálculo dos indicadores

### 5.1 Receita total

Soma dos valores de receita reconhecidos no período selecionado.

### 5.2 Despesa assistencial paga

Soma dos valores efetivamente pagos no período de referência, conforme a regra de competência definida para o indicador.

### 5.3 Sinistralidade paga

Sinistralidade paga = (Despesa assistencial paga / Receita reconhecida) × 100.

**Importante:** a sinistralidade será calculada pela divisão dos valores agregados. Não será utilizada a média simples dos percentuais calculados individualmente por beneficiário, contrato ou prestador.

### 5.4 Sinistralidade incorrida

Será uma evolução futura do modelo. Sua implementação exigirá dados de despesas incorridas, incluindo provisões e ajustes pertinentes. O valor apresentado pelo prestador não será tratado automaticamente como despesa incorrida.

## 6. Integridade e qualidade dos dados

- Todas as chaves estrangeiras deverão referenciar dimensões válidas.
- Valores financeiros deverão utilizar NUMERIC, evitando imprecisão de ponto flutuante.
- Os identificadores sintéticos deverão ser únicos.
- Não serão utilizados dados reais de beneficiários ou pacientes.
- As agregações financeiras deverão respeitar a granularidade das tabelas fato.
- Os relacionamentos entre fatos e dimensões deverão evitar multiplicação indevida de valores.

## 7. Evolução arquitetural

O modelo poderá ser expandido futuramente para contemplar:

- Glosas e recursos de glosa.
- Despesas incorridas e provisões.
- Reembolsos.
- Coparticipação.
- Internações e eventos assistenciais.
- Histórico de alterações cadastrais com dimensão lentamente mutável (SCD).

## 8. Diretriz arquitetural

O PostgreSQL será a fonte oficial dos dados e indicadores.

As consultas SQL serão responsáveis pelos cálculos financeiros oficiais. Python será utilizado para processamento, análise e modelagem preditiva. LangChain e LangGraph serão utilizados para interpretar solicitações, selecionar ferramentas e orquestrar os fluxos inteligentes.

O LLM não deverá substituir as regras de cálculo nem produzir indicadores financeiros sem consultar as fontes analíticas.

---

**Documento:** Healthcare Intelligence Copilot — Data Dictionary  
**Status:** Versão inicial para implementação do modelo físico.