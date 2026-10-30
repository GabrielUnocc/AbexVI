# ABEX VI: Analise de Acidentes em Rodovias Federais da Regiao Sul

Projeto de analise de dados do curso de Sistemas de Informacao da Unochapeco (turma BX, 2026/2).

**Equipe:** Gabriel Victor Rosario, Joao Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi

**Pergunta central:** quais fatores estao associados a gravidade dos acidentes em rodovias federais de SC, PR e RS?

**Fonte dos dados:** [Portal de Dados Abertos da PRF](https://portal.prf.gov.br/dados-abertos-acidentes) — base por ocorrencia (datatran), janeiro a maio de 2026.

---

## Como rodar no Google Colab

Nao e necessario instalar nada, configurar caminhos nem fazer login. Cada notebook clona o repositorio automaticamente na primeira celula.

**Siga a ordem abaixo. Nao pule etapas: cada notebook depende do anterior.**

---

### Notebook 1: EDA de diagnostico

**Link:** [Abrir no Colab](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/01_eda_diagnostico.ipynb)

**O que faz:** carrega a base original da PRF, gera o perfil de qualidade, distribuicoes e primeiras comparacoes por UF, dia da semana, fase do dia e mes. Salva as figuras fig01 a fig07.

**Passos:**
1. Clique no link acima para abrir o notebook no Colab
2. Clique em **Runtime > Run all** (ou `Ctrl+F9`)
3. Aguarde todas as celulas terminarem (a barra de progresso some quando acabar)
4. Confirme que a ultima celula imprimiu algo sem erro

**Nao feche esta aba ainda se for baixar os arquivos. Se fechar, so perdera os outputs temporarios; o proximo notebook funciona normalmente.**

---

### Notebook 2: Pre-processamento

**Link:** [Abrir no Colab](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/02_preprocessamento.ipynb)

**O que faz:** limpa a base, converte tipos, cria variaveis derivadas (hora, faixa horaria, grave_ou_fatal, macrocausa etc.), valida o dominio dos dados e salva a base tratada. Salva a figura fig08.

> Este e o notebook mais importante da ordem: ele gera o arquivo `datatran_sul_tratado.csv` que os notebooks 3 e 4 precisam para rodar.

**Passos:**
1. Clique no link acima para abrir o notebook no Colab (pode ser numa aba nova)
2. Clique em **Runtime > Run all**
3. Aguarde terminar
4. Confirme que uma das celulas imprimiu algo como `"Base salva em data/processed/datatran_sul_tratado.csv"`

---

### Notebook 3: EDA integrada e correlacoes

**Link:** [Abrir no Colab](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/03_eda_integrada_correlacao.ipynb)

**O que faz:** calcula V de Cramer para todas as variaveis explicativas, gera tabelas de contingencia com percentual na linha e indice de letalidade, e produz as visualizacoes para a AV1. Salva as figuras fig09 a fig19.

**Passos:**
1. Clique no link acima para abrir o notebook no Colab
2. Clique em **Runtime > Run all**
3. Aguarde terminar (pode demorar alguns minutos por causa dos graficos)
4. A ultima celula gera automaticamente um arquivo `figuras_nb03.zip` e inicia o download. Salve esse arquivo
5. Extraia o `.zip` e copie as imagens para a pasta `reports/figuras/` do repositorio

---

### Notebook 4: Modelo de classificacao de gravidade

**Link:** [Abrir no Colab](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/04_modelo_gravidade.ipynb)

**O que faz:** treina e avalia tres modelos (regressao logistica, arvore de decisao e random forest) para prever se um acidente resultara em vitima grave ou fatal. Compara com um baseline ingenuo e analisa a importancia das variaveis. Salva as figuras fig20 a fig24.

> Este e o notebook mais demorado. O treinamento do Random Forest pode levar alguns minutos.

**Passos:**
1. Clique no link acima para abrir o notebook no Colab
2. Clique em **Runtime > Run all**
3. Aguarde terminar
4. A ultima celula gera automaticamente um arquivo `figuras_nb04.zip` e inicia o download. Salve esse arquivo
5. Extraia o `.zip` e copie as imagens para a pasta `reports/figuras/` do repositorio

---

## Problemas comuns

**"ModuleNotFoundError" ou "FileNotFoundError" na primeira celula**
A sessao do Colab expirou e o repositorio foi apagado. Clique em **Runtime > Restart and run all** para clonar de novo.

**"KeyError" em alguma coluna**
Voce pulou o Notebook 2 ou ele nao terminou de rodar. Volte ao NB02, rode tudo e tente de novo.

**O download do .zip nao iniciou**
Va ate o painel de arquivos do Colab (icone de pasta na barra lateral esquerda), navegue ate `AbexVI/reports/`, clique com botao direito no arquivo `.zip` e escolha **Download**.

---

## Estrutura do repositorio

```
abex-vi/
├── data/
│   ├── raw/                  # base original da PRF (nunca editar)
│   └── processed/            # base tratada gerada pelo NB02
├── notebooks/                # notebooks numerados em ordem de execucao
├── reports/
│   ├── figuras/              # graficos exportados pelos notebooks
│   ├── decisoes_preprocessamento.csv
│   └── dicionario_dados.md
├── src/
│   └── utils.py              # funcoes auxiliares (cramers_v, perfil_qualidade...)
└── docs/
    └── entregas/             # resumo expandido e outros documentos
```

---

## Dependencias

Todas disponiveis no Google Colab por padrao, sem necessidade de instalacao:

`pandas` `numpy` `matplotlib` `seaborn` `scipy` `scikit-learn`
