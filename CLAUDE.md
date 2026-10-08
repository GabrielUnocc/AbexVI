# CLAUDE.md · ABEX VI: Projeto Integrado III

Análise de acidentes em rodovias federais da Região Sul (SC, PR, RS) com dados abertos da PRF.
Este arquivo orienta o Claude Code sobre o contexto, as regras e as tarefas do projeto. Leia inteiro antes de começar qualquer tarefa.

---

## 1. Contexto

- **Curso:** Sistemas de Informação, Unochapecó, turma BX, 2026/2
- **Componente:** ABEX VI: Projeto Integrado III (Prof. Mateus Henrique Zeiser)
- **Equipe:** Gabriel Victor Rosário, João Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi
- **Tema:** acidentes de trânsito em rodovias federais da Região Sul
- **Pergunta central:** quais fatores estão associados à gravidade dos acidentes? Variável de desfecho: `classificacao_acidente`
- **Variáveis explicativas prioritárias:** `causa_acidente`, `tipo_acidente`, `fase_dia`, `condicao_metereologica`, `tipo_pista`, `tracado_via`, `uso_solo`, `dia_semana`, `horario`, `uf`, `br`
- **Públicos-alvo da devolutiva:** PRF (primário), DNIT (secundário)
- **Fonte:** portal.prf.gov.br/dados-abertos-acidentes, base "por ocorrência" (datatran), CSV
- **Limite declarado:** cobre só acidentes registrados pela PRF em rodovias federais. Não inclui trânsito urbano nem rodovias estaduais. Não há dado de volume de tráfego (exposição), então contagens absolutas não indicam risco. Isso deve aparecer em toda conclusão.

## 2. Regras de trabalho (obrigatórias)

### 2.1 Autoria e uso de IA

1. **O código pode ser gerado; as interpretações e decisões são da equipe.** Em todo notebook, onde houver leitura de gráfico, conclusão, justificativa de escolha ou resposta às perguntas do professor, deixe um bloco markdown marcado assim e **não preencha** mas dê sugestões boas do que fazer, sem problemas:
   ```
   > ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
   > Dica: compare ... / observe /sugestão...
   ```
   Pode incluir uma dica curta do que observar, e a resposta pronta também para aprovação.
2. **Explique o código.** Antes de cada célula de código, uma célula markdown curta dizendo o que ela faz e por quê. O objetivo é que a equipe consiga defender cada linha na apresentação.
3. **Decisões em aberto** (seção 8): não decida sozinho. Pare, apresente as opções com prós e contras e pergunte.
4. **Tratamentos de dados:** proponha a decisão com a evidência, mas registre-a no log de decisões (seção 5.3) para a equipe revisar.

### 2.2 Estilo
- Português do Brasil em textos, comentários, títulos de gráficos e nomes de arquivos.
- **Nunca use travessão (o traço longo, U+2014)** em nenhum texto, comentário, markdown ou rótulo de gráfico. Use vírgula, dois-pontos ou parênteses.
- Gráficos sempre com título, rótulos de eixo e unidade. Preferir taxas e percentuais a contagens absolutas quando comparar grupos de tamanhos diferentes.
- Nomes de variáveis em `snake_case`, em português.

### 2.3 Ambiente
- Python 3 + pandas, numpy, matplotlib, seaborn, scipy, scikit-learn.
- Notebooks `.ipynb` compatíveis com Google Colab (a equipe roda lá). Evite dependências exóticas; se precisar de uma, adicione `!pip install` comentado no topo.
- Caminhos relativos a partir da raiz do repositório.
- Nunca sobrescreva arquivos em `data/raw/`.

## 3. Materiais disponíveis

| Arquivo | O que é |
|---|---|
| `PRF_SUL_2026__Página1.csv` | **Base do projeto.** Recorte datatran 2026 para SC, PR e RS |
| `Aula_06_EDA_codigo_guia.ipynb` | Notebook guia de EDA do professor (checklist de 12 perguntas no final) |
| `Aula_07_Preprocessamento_codigo.ipynb` | Notebook guia de pré-processamento do professor (fluxo e função `registrar_decisao`) |
| `base_eda_abex.csv` | Base didática das aulas (saúde, municípios). **Não usar no projeto**, só como referência de método |
| `Apresentacao_ABEXVI2026_2.pdf`, `Aula02_ABEXVI.pdf`, `Aula03_ABEXVI_pptx.pdf`, `Aulas_ABEX_VI_Mateus.pdf`, `Aulas_ABEX_VI_Mateus_1_.pdf` | Slides das aulas |

**Atenção:** os arquivos `.pdf` dos slides são na verdade arquivos ZIP contendo uma imagem `.jpeg` por slide. Para ler, extraia com `unzip arquivo.pdf -d slides/nome/` e veja as imagens. Consulte-os quando precisar confirmar o que o professor pede em cada etapa.

## 4. O que já se sabe da base (diagnóstico inicial)

Verificado em 24/09/2026. Confirme no notebook de EDA, não confie cegamente.

- **8.703 linhas × 30 colunas.** Uma linha = uma ocorrência (acidente). Chave: `id` (sem duplicatas).
- **Período: 01/01/2026 a 31/05/2026 apenas.** O planejamento previa 2018 em diante (ver decisão D1).
- Distribuição por UF: SC 3.538, PR 3.254, RS 1.911.
- `classificacao_acidente`: Com Vítimas Feridas 6.846 (78,7%), Sem Vítimas 1.406 (16,2%), Com Vítimas Fatais 451 (5,2%). **Classes desbalanceadas.**
- `data_inversa` está como texto `dd/mm/aaaa`; `horario` como texto `hh:mm:ss`.
- `km`, `latitude`, `longitude` usam **vírgula decimal** e estão como texto.
- Ausentes: `regional` (7), `delegacia` (8), `uop` (9). Demais colunas completas.
- Categorias "falsas completas": `condicao_metereologica = "Ignorado"` (63), `sentido_via = "Não Informado"` (20). São ausências disfarçadas.
- `tracado_via` é **multivalorado** separado por `;` e com ordem variável (`"Reta;Declive"` e `"Declive;Reta"` são a mesma coisa). Precisa de tratamento.
- `causa_acidente` tem 65 categorias (muitas raras); `tipo_acidente` tem 16.
- `feridos = feridos_leves + feridos_graves` em todas as linhas (consistente).
- `pessoas` máx. 50, `mortos` máx. 11: extremos plausíveis (ônibus), investigar antes de qualquer decisão.
- `mortos`, `feridos_*`, `ilesos`, `ignorados` **definem** a `classificacao_acidente`. Isso é crítico para o ML (seção 6.4).

## 5. Estrutura do repositório

```
abex-vi/
├── CLAUDE.md
├── README.md
├── data/
│   ├── raw/                  # arquivos originais, nunca editar
│   ├── processed/            # saídas do pré-processamento
│   └── looker/               # CSVs prontos para o Looker Studio
├── materiais/                # notebooks e slides do professor
├── notebooks/
│   ├── 01_eda_diagnostico.ipynb
│   ├── 02_preprocessamento.ipynb
│   ├── 03_eda_integrada_correlacao.ipynb
│   ├── 04_modelo_gravidade.ipynb      # fase 4, condicional
│   └── 05_preparacao_bi.ipynb
├── src/
│   └── utils.py              # funções reutilizáveis (perfil_qualidade, registrar_decisao, cramers_v...)
├── reports/
│   ├── figuras/              # PNGs exportados dos notebooks
│   ├── decisoes_preprocessamento.csv
│   └── dicionario_dados.md
└── docs/
    └── entregas/             # rascunhos de resumo, artigo, roteiro de apresentação
```

### 5.1 Convenções
- Figuras salvas em `reports/figuras/` com nome descritivo (`fig03_gravidade_por_fase_dia.png`, 150 dpi).
- Cada notebook começa com: objetivo, entradas, saídas e as perguntas que responde.
- Cada notebook termina com: resumo do que foi produzido e bloco `✍️ INTERPRETAÇÃO DA EQUIPE`.

### 5.2 Método do professor (seguir à risca)
Fluxo da Aula 07: **abrir a base → EDA → encontrar problemas → investigar → decidir → tratar → validar → salvar**.
- Manter `df_original` intacto e trabalhar numa cópia.
- "Não tratamos um dado apenas porque um comando existe. Primeiro evidência, depois justificativa."
- Outlier sinalizado por IQR **não é removido automaticamente**: verificar se é erro, caso raro real ou informação relevante.
- Não inventar valores. Se a base não permite reconstruir, marcar como ausente ou registrar a limitação.
- Depois do tratamento, repetir a EDA para validar.

### 5.3 Log de decisões
Reutilizar a função do professor, em `src/utils.py`:
```python
registrar_decisao(problema, evidencia, decisao, justificativa, n_afetados)
```
Salvar em `reports/decisoes_preprocessamento.csv`. Toda alteração na base passa por aqui.

## 6. Tarefas por fase

Marque `[x]` ao concluir. Datas conforme cronograma (sujeito a ajuste).

### 6.1 Fase 2: EDA e pré-processamento (agora → 08/10)

**Notebook 01, EDA de diagnóstico** (espelhar a Aula 06, aplicada à base PRF)
- [ ] Carregar com `pd.read_csv` (checar encoding e separador) e guardar `df_original`
- [ ] Responder ao checklist de 12 perguntas da Aula 06 (granularidade, identificadores, tipos, ausentes, duplicatas etc.), cada resposta como bloco da equipe
- [ ] `perfil_qualidade()` (tipo, ausentes, % ausentes, únicos) para todas as colunas
- [ ] `value_counts(dropna=False)` para todas as categóricas; destacar "Ignorado", "Não Informado" e categorias raras
- [ ] Descritivas de `pessoas`, `mortos`, `feridos`, `feridos_graves`, `veiculos`: média, mediana, desvio, quartis, IQR, assimetria
- [ ] Histogramas e boxplots dessas variáveis; listar outliers por IQR sem remover
- [ ] Distribuição de `classificacao_acidente` geral e por UF
- [ ] Primeiras comparações de grupo: acidentes e mortos por UF, dia da semana, fase do dia, mês
- [ ] Lista de problemas encontrados (entrada para o notebook 02)

**Notebook 02, pré-processamento** (espelhar a Aula 07)
- [ ] Converter `data_inversa` para datetime; criar `mes`, `dia_semana_num`, `fim_de_semana`
- [ ] Converter `horario` e criar `hora` (0 a 23) e uma `faixa_horaria` (definir faixas com a equipe)
- [ ] Converter `km`, `latitude`, `longitude` (vírgula → ponto, `pd.to_numeric(errors="coerce")`)
- [ ] Regras de domínio: latitude e longitude dentro da Região Sul, `pessoas >= 1`, contagens não negativas, `pessoas >= mortos + feridos + ilesos + ignorados` (verificar se a soma bate)
- [ ] Coerência da `classificacao_acidente` com as contagens (ex.: "Com Vítimas Fatais" deve ter `mortos > 0`). Registrar inconsistências
- [ ] Padronizar texto (strip, capitalização) nas categóricas
- [ ] `tracado_via`: ordenar os componentes para unificar e criar dummies (`tracado_reta`, `tracado_curva`, `tracado_declive`, `tracado_aclive`, `tracado_intersecao`...). Justificar
- [ ] Tratar "Ignorado" e "Não Informado" como ausência explícita (propor, não aplicar sem confirmação)
- [ ] `regional`, `delegacia`, `uop` ausentes: verificar se dá para recuperar pelo município/UF antes de qualquer preenchimento
- [ ] `causa_acidente`: propor agrupamento em macrocategorias (ex.: comportamento do condutor, via, veículo, ambiente, pedestre). **A equipe aprova o mapeamento**
- [ ] Criar variáveis de gravidade: `teve_morte` (0/1), `grave_ou_fatal` (0/1, com `feridos_graves > 0` ou `mortos > 0`)
- [ ] Validação final (repetir EDA: ausentes, duplicatas, domínio, antes × depois)
- [ ] Salvar `data/processed/datatran_sul_tratado.csv` e o log de decisões
- [ ] Gerar `reports/dicionario_dados.md` (coluna, tipo, descrição, origem: original ou derivada)

### 6.2 Fase 2/3: correlação e EDA integrada (24/09 → 15/10, AV1)

**Notebook 03**
- [ ] Explicar por que Pearson não serve para a maioria das variáveis (quase todas são categóricas)
- [ ] Numéricas: matriz de Spearman entre contagens (`pessoas`, `veiculos`, `mortos`, `feridos`), com interpretação a cargo da equipe
- [ ] Categórica × gravidade: tabelas de contingência com **percentual na linha** e **índice de letalidade** (mortos por 100 acidentes) por categoria
- [ ] Teste qui-quadrado e **V de Cramér** para cada variável explicativa × `classificacao_acidente`; ranking das associações
- [ ] Alertar sobre categorias com poucos casos (frequência esperada < 5) e agrupar ou excluir com justificativa
- [ ] Visualizações para a AV1 (sugestão, ajustar com a equipe):
  - barras 100% empilhadas: gravidade por fase do dia, condição meteorológica, tipo de pista, traçado
  - letalidade por tipo de acidente e por macrocausa (ordenado)
  - heatmap dia da semana × hora (contagem e letalidade)
  - comparação SC × PR × RS normalizada
  - mapa de pontos por latitude/longitude (fatais destacados)
- [ ] Frase-guia para cada gráfico: "correlação/associação não é causa" e "sem volume de tráfego não medimos risco"
- [ ] Bloco final com espaço para as **três a cinco descobertas** da equipe

**Material de apoio à AV1** (em `docs/entregas/`)
- [ ] Esqueleto do resumo simples e do resumo expandido (seções e perguntas-guia, sem texto pronto)
- [ ] Roteiro da apresentação da AV1: demanda, dados, qualidade e tratamento, EDA, próximos passos

### 6.3 TPE 2 (entrega 15/10)
- [ ] Aguardar o enunciado do professor. Não iniciar sem ele.

### 6.4 Fase 4: ML, condicional (22/10 → 29/10)

Só começar depois que a equipe confirmar a decisão D3.

**Notebook 04, classificação de gravidade**
- [ ] Definir alvo com a equipe: multiclasse (`classificacao_acidente`) ou binário (`grave_ou_fatal` / `teve_morte`)
- [ ] **Vazamento de dados:** excluir das features `mortos`, `feridos_leves`, `feridos_graves`, `feridos`, `ilesos`, `ignorados` e qualquer derivada delas, porque elas definem o alvo. Explicar isso no notebook
- [ ] Features somente de contexto conhecido antes do desfecho: condições, via, horário, local, tipo de acidente, causa, `pessoas`, `veiculos`
- [ ] Baseline ingênuo (classe majoritária) para comparação
- [ ] Modelos simples e explicáveis: regressão logística e árvore de decisão; random forest como comparação
- [ ] Divisão estratificada treino/teste; se houver mais de um ano de dados, testar divisão temporal
- [ ] Desbalanceamento: `class_weight="balanced"` e discutir alternativas
- [ ] Métricas: matriz de confusão, precisão, recall e F1 por classe, F1 macro. **Não usar acurácia como métrica principal** (78% é só chutar "feridos")
- [ ] Importância das variáveis e leitura crítica (associação, não causa)

### 6.5 Fase 4: BI e Looker Studio (05/11 → 19/11)

**Notebook 05, preparação para BI**
- [ ] Exportar `data/looker/fato_acidentes.csv` com colunas limpas, nomes legíveis, datas ISO, decimal com ponto, lat/long numéricos
- [ ] Opcional: tabelas agregadas (por UF × mês, por BR × km) se o Looker ficar lento
- [ ] Documentar sugestão de KPIs: total de acidentes, total de mortos, letalidade (mortos por 100 acidentes), % acidentes com vítimas graves ou fatais, trechos críticos (BR + faixa de km)
- [ ] Guia passo a passo em `docs/looker_guia.md` para a equipe montar o dashboard (conectar Google Sheets, campos calculados, filtros por UF, período e BR). **A equipe monta o dashboard**

### 6.6 Fechamento (26/11 devolutiva, 03/12 AV2)
- [ ] Esqueleto do artigo (introdução, método, resultados, discussão, limitações, conclusão) com perguntas-guia por seção
- [ ] Roteiro de storytelling da apresentação final (Knaflic: contexto, conflito, resolução)
- [ ] Checklist de reprodutibilidade: rodar todos os notebooks do zero e conferir as saídas

## 7. Armadilhas conhecidas

- Comparar contagens absolutas entre UFs ou categorias sem normalizar.
- Tratar "Ignorado" como uma condição meteorológica real.
- Concluir causalidade a partir de tabela de contingência ou importância de variável.
- Remover acidentes com muitas pessoas ou mortos por serem outliers (provavelmente são reais e são os mais relevantes).
- Usar contagens de vítimas como feature do modelo de gravidade.
- Esquecer que 5 meses de 2026 podem ter sazonalidade (feriados, chuva de verão) e não representam o ano inteiro.
- Interpretar `uso_solo` sem saber o significado: no datatran, "Sim" indica área urbana e "Não" área rural. Confirmar no dicionário oficial da PRF.

## 8. Decisões em aberto (perguntar à equipe antes)

- **D1, período:** a base atual cobre jan a mai/2026. O planejamento previa 2018 em diante. Opções: (a) seguir só com 2026 e declarar a limitação; (b) baixar anos anteriores do portal da PRF (arquivos `datatran20XX.csv`, filtrar SC/PR/RS e padronizar colunas); (c) usar 2025 completo + 2026 parcial. Impacta tendência temporal e o ML.
- **D2, recorte da pergunta:** gravidade geral, comparação entre estados ou foco em causas/condições da via.
- **D3, ML:** se avança, e qual alvo (multiclasse ou binário).
- **D4, faixas horárias e macrocausas:** definição dos agrupamentos.
- **D5, ausências disfarçadas:** manter "Ignorado"/"Não Informado" como categoria ou converter em NaN.

## 9. Datas-chave

| Data | Entrega |
|---|---|
| 24/09 | TPE 1 (certificado); aula de correlação |
| 01/10 | Semana Acadêmica (sem aula) |
| 08/10 | Oficina de visualizações |
| **15/10** | **AV1** (demanda, preparação, EDA, visualizações) + TPE 2 |
| 22/10 e 29/10 | ML |
| 05/11 a 19/11 | BI e dashboard; TPE 3 em 19/11 |
| 26/11 | Devolutiva |
| **03/12** | **AV2** (solução completa) |

## 10. Referências
Provost e Fawcett (Data Science para Negócios); McKinney (Python para Análise de Dados); Knaflic (Storytelling com Dados); Turban et al. (Business Intelligence); Silva, Peres e Boscarioli (Introdução à Mineração de Dados). Dicionário de dados oficial no portal da PRF.
