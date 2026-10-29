# AATEC - AREA DE AGRARIAS, ENGENHARIAS E TECNOLOGIAS
## CURSO DE SISTEMAS DE INFORMACAO
## ABEX VI: PROJETO INTEGRADO III
## RESUMO EXPANDIDO 1

**Titulo:** Analise de Fatores Associados a Gravidade de Acidentes em Rodovias Federais da Regiao Sul do Brasil

**Integrantes:** Joao Wictor Decarli; Rafael Lucas Rockenbach; Gabriel Victor Rosario; Bernardo Dal Piva Bernardi

**Turma:** BX

**Data:** 08/10/2026

**Palavras-chave:** acidentes de transito; rodovias federais; analise exploratoria de dados; classificacao de gravidade; PRF.

---

## 1 INTRODUCAO

Os acidentes de transito em rodovias federais representam um problema de saude publica e de seguranca viaria de grande relevancia no Brasil. Na Regiao Sul, os estados de Santa Catarina, Parana e Rio Grande do Sul concentram volume expressivo de trafego federal, com caracteristicas geograficas e climaticas diversas que podem influenciar a ocorrencia e a gravidade dos acidentes. Compreender quais fatores estao associados a desfechos mais graves e fundamental para subsidiar acoes preventivas por parte da Policia Rodoviaria Federal (PRF) e do Departamento Nacional de Infraestrutura de Transportes (DNIT).

O projeto parte dos dados abertos de acidentes registrados pela PRF, disponibilizados no portal de dados abertos da instituicao, e aplica tecnicas de analise exploratoria de dados (EDA), pre-processamento e, em etapa posterior, modelagem preditiva para identificar padroes associados a gravidade dos acidentes.

### 1.1 Problema e objetivo do projeto

**Problema investigado:** Quais fatores de contexto, como condicoes da via, horario, causa do acidente e tipo de pista, estao associados a maior gravidade dos acidentes em rodovias federais da Regiao Sul?

**Objetivo geral:** Identificar e quantificar a associacao entre variaveis de contexto e a gravidade dos acidentes de transito registrados pela PRF nos estados de SC, PR e RS em 2026, com o intuito de fornecer subsidios para acoes preventivas da PRF e do DNIT.

**Objetivos especificos:**
- Caracterizar a base de dados da PRF quanto a qualidade, completude e distribuicao das variaveis;
- Realizar analise exploratoria descritiva e investigar relacoes entre variaveis explicativas e a gravidade dos acidentes;
- Construir um modelo de classificacao para prever se um acidente resultara em vitima grave ou fatal, usando apenas variaveis de contexto conhecidas antes do desfecho.

---

## 2 BASE DE DADOS E PROCEDIMENTOS METODOLOGICOS

### 2.1 Origem e caracterizacao dos dados

| Item | Descricao |
|---|---|
| Fonte dos dados | Portal de dados abertos da Policia Rodoviaria Federal: portal.prf.gov.br/dados-abertos-acidentes |
| Periodo | 01/01/2026 a 31/05/2026 (5 meses) |
| Formato | CSV (separador ponto e virgula, encoding UTF-8) |
| Dimensao inicial | 8.703 linhas x 30 colunas |
| Unidade de analise | Uma ocorrencia de acidente de transito em rodovia federal |
| Bases integradas | Nao aplicavel: utilizou-se apenas o recorte da Regiao Sul (SC, PR e RS) extraido da base "por ocorrencia" (datatran) |

Fonte: elaborada pelos autores.

A base e composta por uma linha por ocorrencia de acidente. O identificador unico e a coluna `id`, sem duplicatas. A distribuicao geografica e: Santa Catarina com 3.538 registros (40,6%), Parana com 3.254 (37,4%) e Rio Grande do Sul com 1.911 (22,0%).

### 2.2 Limpeza e pre-processamento dos dados

O pre-processamento seguiu o fluxo proposto pelo professor: abrir a base, realizar EDA, identificar problemas, investigar, decidir, tratar e validar. Todas as decisoes foram registradas em log com justificativa e quantidade de registros afetados.

Os principais procedimentos realizados foram:

**Conversao de tipos:** A coluna `data_inversa` (formato texto `dd/mm/aaaa`) foi convertida para datetime, permitindo extrair `mes` (1 a 5) e `dia_semana_num`. A coluna `horario` (texto `hh:mm:ss`) gerou a variavel `hora` (0 a 23). As colunas `km`, `latitude` e `longitude` usavam virgula decimal e estavam como texto; foram convertidas para numerico com `pd.to_numeric(errors="coerce")`.

**Criacao de variaveis:** Foram criadas as variaveis `fim_de_semana` (binaria), `faixa_horaria` (Madrugada 0-5h, Manha 6-11h, Tarde 12-17h, Noite 18-23h) e duas variaveis de desfecho: `teve_morte` (1 se `mortos > 0`) e `grave_ou_fatal` (1 se `feridos_graves > 0` ou `mortos > 0`), usada como alvo do modelo preditivo.

**Validacao de dominio:** Verificou-se que as coordenadas geograficas estavam dentro da Regiao Sul (latitude -35 a -22, longitude -57 a -44), que `pessoas >= 1` em todos os registros e que a soma de mortos, feridos e ilesos era consistente com o total de pessoas. Nenhum registro precisou ser removido por violacao de dominio. A coerencia entre `classificacao_acidente` e as contagens de vitimas foi verificada sem inconsistencias.

**Ausencias:** As colunas `regional` (7 ausentes), `delegacia` (8) e `uop` (9) tiveram recuperacao tentada via moda do municipio, sem sucesso para os casos restantes. As categorias `condicao_metereologica = "Ignorado"` (63 registros) e `sentido_via = "Nao Informado"` (20 registros) foram convertidas para ausencia explicita (NaN), pois representam ausencia disfarçada de informacao.

**Variavel multivalorada:** `tracado_via` continha multiplos valores separados por ponto e virgula, com ordem variavel. Foi normalizado (componentes ordenados alfabeticamente) e expandido em variaveis dummies binarias: `tracado_reta`, `tracado_curva`, `tracado_declive`, `tracado_aclive`, `tracado_intersecao_de_vias`, `tracado_ponte`, `tracado_rotatoria`, `tracado_viaduto`, entre outras.

**Agrupamento de causas:** A coluna `causa_acidente` apresentava 65 categorias, muitas com baixa frequencia. As causas foram agrupadas em 8 macrocategorias: Falha de atencao ou reacao, Comportamento de risco, Infracao de transito, Alcool ou substancias, Condicao do veiculo, Condicao da via ou ambiente, Fator externo, Pedestre ou ciclista.

Apos o pre-processamento, a base passou de 30 para 51 colunas, sem remocao de linhas.

### 2.3 Analise Exploratoria de Dados (EDA)

A EDA foi dividida em dois notebooks. O primeiro (Notebook 01) focou no diagnostico da qualidade dos dados: perfil de qualidade de todas as colunas, distribuicoes univariadas das variaveis numericas (histogramas, boxplots, medidas descritivas), frequencias das variaveis categoricas e identificacao de ausencias e anomalias.

O segundo notebook de EDA (Notebook 03) aprofundou as relacoes entre variaveis: tabelas de contingencia com percentual na linha e indice de letalidade (mortos por 100 acidentes) para cada variavel explicativa cruzada com `classificacao_acidente`, teste qui-quadrado e V de Cramer para rankear as associacoes, e visualizacoes comparativas (barras 100% empilhadas, heatmap hora x dia da semana, comparacao entre UFs). As analises priorizaram as variaveis listadas no objetivo do projeto: `causa_acidente`, `tipo_acidente`, `fase_dia`, `condicao_metereologica`, `tipo_pista`, `tracado_via`, `uso_solo`, `dia_semana`, `horario`, `uf` e `br`.

### 2.4 Ferramentas e organizacao do trabalho

O projeto foi desenvolvido em Python 3 com os notebooks executados no Google Colab. As principais bibliotecas utilizadas foram: `pandas` e `numpy` para manipulacao de dados, `matplotlib` e `seaborn` para visualizacao, `scipy` para testes estatisticos (qui-quadrado) e `scikit-learn` para modelagem preditiva. O repositorio esta organizado com separacao entre dados brutos (`data/raw/`, nunca sobrescritos), dados processados (`data/processed/`), notebooks numerados (`notebooks/`) e figuras exportadas (`reports/figuras/`).

---

## 3 RESULTADOS PARCIAIS E DISCUSSAO

### 3.1 Diagnostico da qualidade dos dados

A base apresentou qualidade geral elevada. Dos 30 campos originais, apenas 3 tinham ausencias reais (`regional`, `delegacia`, `uop`), todas com menos de 0,1% de registros afetados. Outros 2 campos apresentavam ausencias disfarçadas em categorias como "Ignorado" e "Nao Informado", totalizando 83 registros (menos de 1% da base). Nao foram encontradas duplicatas no identificador `id`.

Os principais problemas identificados e tratados foram:

- Tipos incorretos: `data_inversa`, `horario`, `km`, `latitude` e `longitude` armazenados como texto;
- Variavel multivalorada: `tracado_via` com valores compostos separados por ponto e virgula;
- Alta cardinalidade: `causa_acidente` com 65 categorias, dificultando analise e modelagem;
- Desbalanceamento do alvo: a classe "Com Vítimas Fatais" representa apenas 5,2% dos registros.

Nenhum registro foi removido da base. A decisao de manter todos os registros, incluindo os com valores extremos em `pessoas` (maximo 50) e `mortos` (maximo 11), baseou-se na evidencia de que esses casos correspondem provavelmente a acidentes reais com onibus e sao justamente os mais relevantes para o objetivo do projeto.

### 3.2 Resultados da analise exploratoria

No periodo analisado (jan-mai/2026), foram registrados 8.703 acidentes em rodovias federais da Regiao Sul, resultando em 531 mortos, 2.165 feridos graves e 7.737 feridos leves. A classificacao geral dos acidentes foi: Com Vitimas Feridas 6.846 (78,7%), Sem Vitimas 1.406 (16,2%) e Com Vitimas Fatais 451 (5,2%).

**[INSERIR AQUI fig03_classificacao_acidente.png]**

FIGURA 1 - Distribuicao da classificacao dos acidentes por UF (SC, PR, RS)

Fonte: elaborada pelos autores com base nos dados da PRF (2026).

A distribuicao por estado mostrou proporcoes similares de gravidade entre SC, PR e RS, sem distorcoes expressivas entre as unidades federativas, embora o Rio Grande do Sul concentre proporcionalmente menos acidentes no periodo.

A analise por tipo de acidente revelou que a colisao traseira e o tipo mais frequente (1.665 registros, 19,1%), seguida pela saida de leito carrocavel (1.414, 16,3%) e colisao transversal (1.266, 14,5%). Contudo, ao calcular o indice de letalidade (mortos por 100 acidentes), o quadro muda: a **colisao frontal** e o tipo mais letal, com 37,1 mortos por 100 acidentes, seguida pelo **atropelamento de pedestre** (30,0). Esses dois tipos, embora nao sejam os mais frequentes, concentram o maior risco de morte.

**[INSERIR AQUI fig08_letalidade_macrocausa.png ou grafico de letalidade por tipo de acidente do NB03]**

FIGURA 2 - Indice de letalidade por tipo de acidente (mortos por 100 acidentes)

Fonte: elaborada pelos autores com base nos dados da PRF (2026).

Quanto as macrocausas, a categoria "Falha de atencao ou reacao" e responsavel por 4.652 acidentes (53,5% do total), consolidando as causas comportamentais como o principal grupo. Comportamento de risco (1.440, 16,5%) e a segunda categoria mais frequente, seguida pelo grupo "Outras" (880, 10,1%).

A analise do tipo de pista mostrou que acidentes em **pista simples** tem maior proporcao de desfechos graves ou fatais (29,1%) em comparacao com pista dupla (20,2%) e multipla (21,8%), sugerindo que a infraestrutura da via esta associada a gravidade dos acidentes. De forma analoga, acidentes em area rural (`uso_solo = "Nao"`) apresentaram proporcao de desfechos graves/fatais de 26,6%, contra 22,0% em area urbana, o que e coerente com o maior risco em vias interurbanas sem separacao de faixas e com velocidades mais altas.

A analise por fase do dia indicou que o periodo de **amanhecer** concentra a maior proporcao de acidentes graves ou fatais (29,1%), seguido pela plena noite (26,6%). O pleno dia, apesar de concentrar o maior numero absoluto de acidentes, apresenta a menor proporcao de desfechos graves (23,0%).

### 3.3 Relacoes, cruzamentos e insights iniciais

As analises de associacao (V de Cramer) entre cada variavel explicativa e a `classificacao_acidente` indicaram que as variaveis com maior associacao sao `tipo_acidente` e `causa_acidente` (via `macrocausa`), seguidas de `fase_dia` (V = 0,11) e `uso_solo` (V = 0,09). `tipo_pista` apresentou V de Cramer de apenas 0,05, abaixo dessas quatro variaveis. Todas as associacoes foram estatisticamente significativas pelo qui-quadrado, mas os valores de V de Cramer sao baixos a moderados, indicando que nenhuma variavel isolada determina a gravidade.

Um insight relevante e o contraste entre frequencia e letalidade: os tipos de acidente mais comuns (colisao traseira, saida de leito carrocavel) nao sao os mais letais. A colisao frontal representa apenas 6,1% dos casos registrados, mas e responsavel por 37,3% de todas as mortes do periodo. Esse contraste entre frequencia e impacto sugere que acoes preventivas da PRF e do DNIT devem priorizar a reducao de colisoes frontais (sinalizacao, barreiras fisicas de separacao de faixas, fiscalizacao de ultrapassagens proibidas) mesmo que o numero absoluto de casos seja menor.

**Importante:** associacao estatistica nao implica causalidade. Alem disso, a ausencia de dados de volume de trafego impede calcular o risco relativo por quilometro percorrido. Todos os percentuais e indices de letalidade refletem os registros de acidentes, nao o risco de um veiculo ser envolvido em acidente ao percorrer determinado trecho.

### 3.4 Limitacoes identificadas

- **Periodo reduzido:** a base cobre apenas janeiro a maio de 2026 (5 meses). Eventos sazonais como feriados prolongados de verao e chuvas intensas no inicio do ano podem distorcer os padroes. O periodo nao representa um ano completo.
- **Ausencia de volume de trafego:** sem dados de fluxo de veiculos por trecho, nao e possivel calcular taxa de acidentes por quilometro percorrido. Comparacoes entre rodovias ou estados com base em contagens absolutas nao refletem risco real.
- **Cobertura restrita:** a base inclui apenas acidentes registrados pela PRF em rodovias federais. Acidentes em rodovias estaduais, municipais e vias urbanas nao estao representados.
- **Qualidade do registro:** variaveis como `causa_acidente` dependem do julgamento do policial no momento do registro, o que pode introduzir subjetividade e variacoes entre regioes ou turnos.
- **Desbalanceamento do alvo para modelagem:** o alvo binario `grave_ou_fatal` apresenta apenas 24,6% de casos positivos. Sem compensacao (como `class_weight='balanced'`), um modelo trivial que sempre prediz "nao grave" ja atingiria 75% de acuracia, tornando essa metrica inutil. Por isso, o projeto priorizou F1 macro e recall da classe positiva como metricas principais.
- **Features pos-acidente:** `tipo_acidente` e `causa_acidente` sao registrados pela PRF apos o acidente, nao sendo variaveis de contexto pre-evento. O modelo tem valor descritivo e associativo, mas nao prediz gravidade antes do acidente acontecer. Para uso operacional preventivo em tempo real, essas features deveriam ser excluidas.

---

## 4 ANDAMENTO DO PROJETO E PROXIMAS ETAPAS

**Concluido ate o momento:**
- Notebook 01: EDA de diagnostico (perfil de qualidade, distribuicoes, ausentes, duplicatas, primeiras comparacoes por UF, dia da semana, fase do dia e mes);
- Notebook 02: pre-processamento completo (conversao de tipos, criacao de variaveis, validacao de dominio, tratamento de ausencias disfarçadas, normalizacao de `tracado_via`, agrupamento de macrocausas, criacao de `grave_ou_fatal`);
- Notebook 03: EDA integrada e de correlacao (V de Cramer, tabelas de contingencia com percentual na linha, indice de letalidade por variavel, visualizacoes para a AV1);
- Base tratada salva em `data/processed/datatran_sul_tratado.csv` (8.703 linhas x 51 colunas);
- Log de decisoes de pre-processamento registrado em `reports/decisoes_preprocessamento.csv`;
- Dicionario de dados em `reports/dicionario_dados.md`.
- Notebook 04: modelo de classificacao binaria criado (baseline, regressao logistica, arvore de decisao, random forest). Execucao e interpretacao pendentes.

**Em andamento:**
- Execucao e interpretacao dos resultados do Notebook 04 (modelo ML).

**Proximas etapas:**
- Interpretar os resultados do modelo (F1 macro, recall da classe grave/fatal, importancia das features);
- Notebook 05: preparacao da base para o Looker Studio (exportacao de `fato_acidentes.csv`, tabelas agregadas, KPIs);
- Montagem do dashboard no Looker Studio;
- Redacao do artigo final e preparacao da apresentacao (AV2 em 03/12/2026).

---

## 5 CONSIDERACOES PARCIAIS

O trabalho realizado ate o momento permitiu caracterizar com precisao a base de dados da PRF para a Regiao Sul e identificar os principais padroes associados a gravidade dos acidentes. Os resultados da EDA indicam que o tipo de acidente, especialmente a colisao frontal e o atropelamento de pedestre, e a variavel mais fortemente associada a desfechos fatais, mesmo representando uma parcela minoritaria dos casos. A infraestrutura da via (pista simples versus dupla) e o contexto (area rural versus urbana) tambem apresentam associacao relevante com a gravidade.

O objetivo geral do projeto e identificar fatores associados a gravidade para subsidiar acoes preventivas da PRF e do DNIT. As evidencias obtidas ate aqui apontam direcoes claras para essa discussao: a reducao de colisoes frontais e o monitoramento de trechos de pista simples em area rural merecem atencao prioritaria. As proximas etapas, especialmente a modelagem preditiva e o dashboard interativo, permitirao aprofundar e comunicar esses achados de forma mais acessivel aos publicos-alvo.

---

## DECLARACAO DE USO DE INTELIGENCIA ARTIFICIAL

Foi utilizada a ferramenta Claude Code (Anthropic) para geracao de codigo Python, estruturacao dos notebooks e sugestao de analises. Os autores revisaram criticamente todo o conteudo gerado, preencheram os blocos de interpretacao e assumem integral responsabilidade pelo conteudo final do trabalho.

---

## REFERENCIAS

POLICIA RODOVIARIA FEDERAL. Dados Abertos: Acidentes. 2026. Disponivel em: portal.prf.gov.br/dados-abertos-acidentes. Acesso em: 24 set. 2026.

PROVOST, F.; FAWCETT, T. Data Science para Negocios. Rio de Janeiro: Alta Books, 2016.

MCKINNEY, W. Python para Analise de Dados. 2. ed. Sao Paulo: Novatec, 2019.

KNAFLIC, C. N. Storytelling com Dados. Rio de Janeiro: Alta Books, 2019.

---

## CHECKLIST ANTES DA ENTREGA

- [x] A origem da base de dados esta identificada.
- [x] O texto descreve o que foi efetivamente realizado em EDA e pre-processamento.
- [ ] Graficos e tabelas relevantes estao inseridos e interpretados no texto. *(inserir as figuras nos locais indicados)*
- [x] O andamento e as proximas etapas estao claramente registrados.
- [x] A declaracao de uso de IA foi preenchida.
- [x] As referencias citadas no texto estao listadas ao final.
- [ ] Todos os textos de orientacao do modelo foram removidos. *(este checklist deve ser removido na versao final)*

---

> **Nota para a equipe:** Este documento foi gerado com base nos dados reais da analise.
> Antes de entregar, a equipe deve:
> 1. Inserir as figuras nos locais marcados com [INSERIR AQUI ...], usando os PNGs de `reports/figuras/`
> 2. Revisar e ajustar as interpretacoes nos trechos que precisam de julgamento da equipe
> 3. Copiar o conteudo para o .docx do professor e aplicar a formatacao original
> 4. Remover esta nota e o checklist da versao entregue
