# ABEX VI: Analise de Acidentes em Rodovias Federais da Regiao Sul

Projeto de analise de dados do curso de Sistemas de Informacao da Unochapeco (turma BX, 2026/2).

**Equipe:** Gabriel Victor Rosario, Joao Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi

**Pergunta central:** quais fatores estao associados a gravidade dos acidentes em rodovias federais de SC, PR e RS?

**Fonte dos dados:** [Portal de Dados Abertos da PRF](https://portal.prf.gov.br/dados-abertos-acidentes) — base por ocorrencia (datatran), janeiro a maio de 2026.

---

## Como rodar no Google Colab

Nao e necessario instalar nada nem configurar caminhos. Cada notebook clona o repositorio automaticamente.

**Abra cada notebook no Colab em ordem:**

| Ordem | Notebook | O que faz |
|---|---|---|
| 1 | [01_eda_diagnostico.ipynb](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/01_eda_diagnostico.ipynb) | EDA de diagnostico: qualidade, distribuicoes, primeiras comparacoes |
| 2 | [02_preprocessamento.ipynb](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/02_preprocessamento.ipynb) | Limpeza, conversao de tipos, criacao de variaveis, base tratada |
| 3 | [03_eda_integrada_correlacao.ipynb](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/03_eda_integrada_correlacao.ipynb) | V de Cramer, tabelas de contingencia, visualizacoes |
| 4 | [04_modelo_gravidade.ipynb](https://colab.research.google.com/github/GabrielUnocc/AbexVI/blob/master/notebooks/04_modelo_gravidade.ipynb) | Modelo de classificacao de gravidade (ML) |

Em cada notebook: **Runtime > Run all** e aguardar terminar antes de abrir o proximo.

> A ordem importa: o NB02 gera a base tratada que os NB03 e NB04 precisam.

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

Todas disponiveis no Google Colab por padrao:

`pandas` `numpy` `matplotlib` `seaborn` `scipy` `scikit-learn`
