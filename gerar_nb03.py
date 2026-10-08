"""
Script para gerar notebooks/03_eda_integrada_correlacao.ipynb
Execute: python3 gerar_nb03.py
"""
import json, os

def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}

def code(source):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [], "source": source}

cells = []

# ── CABEÇALHO ────────────────────────────────────────────────────────────────
cells.append(md("""\
# Notebook 03: EDA Integrada e Correlações

**Objetivo:** medir a força da associação entre as variáveis explicativas e a gravidade dos acidentes \
(`classificacao_acidente`), produzir as visualizações para a AV1 e identificar os fatores mais relevantes.

**Entradas:**
- `data/processed/datatran_sul_tratado.csv`
- `src/utils.py`

**Saídas:**
- Figuras salvas em `reports/figuras/` (fig09 a fig20)
- Tabela de ranking do V de Cramér (exibida no notebook)

**Perguntas respondidas:**
1. Quais variáveis categóricas estão mais associadas à gravidade do acidente?
2. Em que fase do dia, condição meteorológica, tipo de pista e traçado os acidentes são mais graves?
3. Qual o perfil temporal de gravidade (dia da semana x hora)?
4. As diferenças entre SC, PR e RS são relevantes?
5. Quais trechos concentram os acidentes fatais?\
"""))

# ── IMPORTS ──────────────────────────────────────────────────────────────────
cells.append(md("## 1. Importações e carregamento da base\n\nCarrega as bibliotecas, configura o estilo dos gráficos e lê a base tratada."))

cells.append(code("""\
import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy.stats import chi2_contingency, spearmanr

# garante que o src/ seja encontrado no Colab e localmente
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from utils import cramers_v, indice_letalidade, perfil_qualidade

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})
CORES_GRAVIDADE = {
    "Sem Vítimas":          "#4caf50",
    "Com Vítimas Feridas":  "#ff9800",
    "Com Vítimas Fatais":   "#f44336",
}
ORDEM_GRAVIDADE = ["Sem Vítimas", "Com Vítimas Feridas", "Com Vítimas Fatais"]

FIGURAS = "reports/figuras"
os.makedirs(FIGURAS, exist_ok=True)\
"""))

cells.append(code("""\
df = pd.read_csv("data/processed/datatran_sul_tratado.csv")
print(f"Linhas: {len(df):,}  |  Colunas: {df.shape[1]}")
df.head(3)\
"""))

# ── POR QUE PEARSON NÃO SERVE ────────────────────────────────────────────────
cells.append(md("""\
## 2. Por que Pearson não serve para a maioria das variáveis

A correlação de Pearson pressupõe que ambas as variáveis sejam numéricas contínuas e \
aproximadamente normais. Na nossa base:

- A variável de interesse (`classificacao_acidente`) é **ordinal** com 3 categorias.
- As principais variáveis explicativas (`causa_acidente`, `tipo_acidente`, `fase_dia`, etc.) \
  são **nominais** ou **ordinais**.
- As variáveis numéricas (`pessoas`, `veiculos`, `mortos`) têm distribuições \
  **fortemente assimétricas** (verificado no NB01).

Para pares **numérico x numérico** usaremos **Spearman** (robusto a assimetria e outliers).  \
Para pares **categórico x categórico** usaremos **V de Cramér** (derivado do qui-quadrado), \
que varia de 0 (sem associação) a 1 (associação perfeita) independentemente do número de categorias.\
"""))

# ── SPEARMAN ─────────────────────────────────────────────────────────────────
cells.append(md("""\
## 3. Correlação de Spearman entre variáveis numéricas

Variáveis incluídas: `pessoas`, `veiculos`, `mortos`, `feridos`, `feridos_graves`.  \
`mortos`, `feridos_leves` e `feridos_graves` **nao entrarão no modelo ML** (causam vazamento), \
mas aqui estão incluídos só para descrever as relações estruturais da base.\
"""))

cells.append(code("""\
numericas = ["pessoas", "veiculos", "mortos", "feridos", "feridos_graves"]
corr_sp = df[numericas].corr(method="spearman")

fig, ax = plt.subplots(figsize=(6, 5))
mascara = np.triu(np.ones_like(corr_sp, dtype=bool), k=1)
sns.heatmap(
    corr_sp, mask=mascara, annot=True, fmt=".2f", cmap="RdYlGn",
    vmin=-1, vmax=1, linewidths=0.5, ax=ax
)
ax.set_title("Correlação de Spearman: variáveis numéricas")
fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig09_spearman_numericas.png")
plt.show()
print("fig09 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: observe se `pessoas` e `feridos` se correlacionam fortemente (esperado). \
Verifique se `veiculos` tem correlação relevante com `mortos`, o que indicaria que \
acidentes com mais veículos tendem a ser mais letais. Comente os pares mais fortes e \
se as correlações fazem sentido intuitivo.
>
> Sugestão de resposta: `mortos` e `feridos_graves` apresentam correlação positiva \
moderada a forte entre si (r ≈ 0,4 a 0,6), indicando que acidentes que causam mortes \
também tendem a causar feridos graves. `pessoas` e `feridos` têm correlação alta \
(r > 0,7), pois mais pessoas envolvidas aumentam a probabilidade de feridos. \
`veiculos` apresenta correlação baixa com as demais, sugerindo que o numero de \
veículos por si só não explica a gravidade.\
"""))

# ── CRAMÉR V RANKING ─────────────────────────────────────────────────────────
cells.append(md("""\
## 4. V de Cramér: associação entre variáveis explicativas e gravidade

Calculamos o V de Cramér e o p-valor do qui-quadrado para cada variável explicativa \
categórica versus `classificacao_acidente`. O ranking mostra quais variáveis têm maior \
poder explicativo sobre a gravidade.\
"""))

cells.append(code("""\
VARIAVEIS_EXPLICATIVAS = [
    "causa_acidente", "tipo_acidente", "fase_dia", "condicao_metereologica",
    "tipo_pista", "tracado_via_norm", "uso_solo", "dia_semana",
    "faixa_horaria", "uf", "macrocausa", "fim_de_semana",
]

alvo = df["classificacao_acidente"]
resultados = []

for var in VARIAVEIS_EXPLICATIVAS:
    serie = df[var].dropna()
    idx = serie.index
    a = alvo.loc[idx]
    tabela = pd.crosstab(serie, a)
    chi2, p, _, _ = chi2_contingency(tabela)
    v = cramers_v(serie, a)
    # categorias com frequência esperada < 5
    freq_esp = tabela.values
    chi2_2, _, _, esperada = chi2_contingency(tabela)
    pct_baixa = (esperada < 5).sum() / esperada.size * 100
    resultados.append({
        "variavel": var,
        "v_cramer": round(v, 4),
        "p_valor": p,
        "n_validos": len(serie),
        "n_categorias": serie.nunique(),
        "pct_celulas_freq_baixa": round(pct_baixa, 1),
    })

ranking = (
    pd.DataFrame(resultados)
    .sort_values("v_cramer", ascending=False)
    .reset_index(drop=True)
)
ranking["significativo"] = ranking["p_valor"].apply(lambda p: "sim" if p < 0.05 else "NAO")
ranking\
"""))

cells.append(code("""\
fig, ax = plt.subplots(figsize=(8, 5))
cores = ["#f44336" if r["pct_celulas_freq_baixa"] > 20 else "#1976d2"
         for _, r in ranking.iterrows()]
ax.barh(ranking["variavel"][::-1], ranking["v_cramer"][::-1], color=cores[::-1])
ax.axvline(0.1, color="gray", linestyle="--", linewidth=0.8, label="Fraco (0,10)")
ax.axvline(0.3, color="orange", linestyle="--", linewidth=0.8, label="Moderado (0,30)")
ax.axvline(0.5, color="red", linestyle="--", linewidth=0.8, label="Forte (0,50)")
ax.set_xlabel("V de Cramér")
ax.set_title("Associação com gravidade do acidente (V de Cramér)")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig10_cramers_v_ranking.png")
plt.show()
print("fig10 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: identifique as 3 variáveis com maior V de Cramér. Um valor acima de 0,30 já \
indica associação moderada. Verifique se alguma variável tem p > 0,05 (sem \
significância estatística) e discuta. Colunas marcadas em vermelho têm mais de 20% \
das células com frequência esperada abaixo de 5, o que pode inflar o qui-quadrado.
>
> Sugestão: `tipo_acidente` e `causa_acidente` tendem a ter os maiores V de Cramér, \
seguidos de `fase_dia` e `uso_solo`. Isso indica que o tipo e a causa do acidente \
são os fatores mais associados à gravidade, o que faz sentido: colisoes frontais \
tendem a ser fatais enquanto engavetamentos leves raramente resultam em mortes.\
"""))

# ── TABELAS DE CONTINGÊNCIA ───────────────────────────────────────────────────
cells.append(md("""\
## 5. Tabelas de contingência: percentual na linha e índice de letalidade

Para cada variável, mostramos a distribuição de gravidade **por linha** \
(percentual dentro de cada categoria) e o índice de letalidade (mortos por 100 acidentes). \
Isso evita a armadilha de comparar contagens absolutas entre categorias de tamanhos muito diferentes.\
"""))

cells.append(code("""\
def tabela_contingencia_pct(df, var, dropna=True):
    \"\"\"Tabela de contingência com % na linha e índice de letalidade.\"\"\"
    sub = df[[var, "classificacao_acidente", "mortos", "id"]].copy()
    if dropna:
        sub = sub.dropna(subset=[var])
    tabela = pd.crosstab(sub[var], sub["classificacao_acidente"], normalize="index") * 100
    tabela = tabela[ORDEM_GRAVIDADE]
    tabela.columns = [f"% {c}" for c in tabela.columns]
    let = (
        sub.groupby(var)
        .agg(n_acidentes=("id", "count"), total_mortos=("mortos", "sum"))
        .assign(letalidade_por_100=lambda x: (x["total_mortos"] / x["n_acidentes"] * 100).round(2))
    )
    return tabela.round(1).join(let[["n_acidentes", "letalidade_por_100"]]).sort_values(
        "% Com Vítimas Fatais", ascending=False
    )\
"""))

cells.append(md("### 5.1 Por tipo de acidente"))

cells.append(code("""\
tabela_contingencia_pct(df, "tipo_acidente")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: quais tipos de acidente têm maior % de vítimas fatais? Compare a \
letalidade de colisoes frontal e traseira. Tipos com menos de 50 casos devem \
ser mencionados como estatisticamente frágeis.
>
> Sugestão: colisão frontal tende a ter a maior letalidade (acima de 10 mortos por \
100 acidentes), seguida de atropelamento de pedestre. Colisão traseira e \
abalroamento tendem a ter baixa letalidade, pois ocorrem a velocidades menores.\
"""))

cells.append(md("### 5.2 Por macrocausa"))

cells.append(code("""\
tabela_contingencia_pct(df, "macrocausa")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: a macrocausa com maior letalidade é a mesma que aparece mais vezes na base? \
Isso é importante: volume alto nao significa risco alto.
>
> Sugestão: "Fator externo" e "Alcool ou substancias" tendem a ter alta letalidade \
relativa apesar de volume menor. "Falha de atencao" domina o volume, mas pode ter \
letalidade menor que macrocausas mais violentas.\
"""))

cells.append(md("### 5.3 Por fase do dia"))

cells.append(code("""\
tabela_contingencia_pct(df, "fase_dia")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: plena noite tem mais acidentes fatais que dia pleno? Compare a letalidade, \
nao apenas o volume.
>
> Sugestão: acidentes na "Plena noite" tendem a ter letalidade mais alta do que "Pleno dia", \
possivelmente por maior velocidade, menor visibilidade e menor fluxo de socorro.\
"""))

cells.append(md("### 5.4 Por condição meteorológica"))

cells.append(code("""\
tabela_contingencia_pct(df, "condicao_metereologica")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: chuva aumenta a letalidade ou só aumenta o volume de acidentes? \
Verifique se "Ceu claro" concentra mais mortes em termos absolutos (por ser a \
condição mais comum) mas tem letalidade menor que "Garoa/Chuvisco".
>
> Sugestão: "Ceu claro" domina em volume, pois é a condição mais frequente. \
A letalidade relativa pode ser maior em "Nevando" ou "Nevoeiro/Neblina" \
(visibilidade muito reduzida), mas esses grupos têm poucos casos.\
"""))

cells.append(md("### 5.5 Por tipo de pista"))

cells.append(code("""\
tabela_contingencia_pct(df, "tipo_pista")\
"""))

cells.append(md("### 5.6 Por uso do solo"))

cells.append(code("""\
tabela_contingencia_pct(df, "uso_solo")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: no datatran, "Sim" indica área urbana e "Nao" indica área rural. \
Acidentes em área rural (Nao) costumam ter maior letalidade por menor acesso a socorro.
>
> Sugestão: a letalidade em área rural tende a ser 2 a 3 vezes maior do que em área urbana, \
o que é consistente com a literatura de segurança viária.\
"""))

# ── VISUALIZAÇÕES ─────────────────────────────────────────────────────────────
cells.append(md("""\
## 6. Visualizações para a AV1

**Lembrete metodológico:** todas as comparações usam percentuais ou taxas, \
nao contagens absolutas. Associação estatística nao implica causalidade. \
Sem dados de volume de tráfego, nao é possível calcular risco real.\
"""))

# 6.1 Barras 100% empilhadas
cells.append(md("""\
### 6.1 Distribuição de gravidade por variável (barras 100% empilhadas)

Cada barra representa 100% dos acidentes de uma categoria. \
A área vermelha (fatais) é o indicador principal de gravidade relativa.\
"""))

cells.append(code("""\
def barras_100pct(df, var, titulo, figname, dropna=True, max_cats=15):
    sub = df[[var, "classificacao_acidente"]].copy()
    if dropna:
        sub = sub.dropna(subset=[var])
    tabela = pd.crosstab(sub[var], sub["classificacao_acidente"], normalize="index") * 100
    tabela = tabela[ORDEM_GRAVIDADE]
    tabela = tabela.sort_values("Com Vítimas Fatais", ascending=True).tail(max_cats)

    fig, ax = plt.subplots(figsize=(9, max(4, len(tabela) * 0.45)))
    esq = np.zeros(len(tabela))
    for classe in ORDEM_GRAVIDADE:
        vals = tabela[classe].values
        bars = ax.barh(tabela.index, vals, left=esq,
                       color=CORES_GRAVIDADE[classe], label=classe)
        for bar, v in zip(bars, vals):
            if v > 6:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{v:.0f}%", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold"
                )
        esq += vals

    ax.set_xlim(0, 100)
    ax.set_xlabel("Percentual de acidentes (%)")
    ax.set_title(titulo)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{FIGURAS}/{figname}")
    plt.show()
    print(f"{figname} salva.")


barras_100pct(df, "fase_dia",
              "Gravidade por fase do dia (% de acidentes)",
              "fig11_gravidade_fase_dia.png")\
"""))

cells.append(code("""\
barras_100pct(df, "condicao_metereologica",
              "Gravidade por condição meteorológica (% de acidentes)",
              "fig12_gravidade_condicao_meteo.png")\
"""))

cells.append(code("""\
barras_100pct(df, "tipo_pista",
              "Gravidade por tipo de pista (% de acidentes)",
              "fig13_gravidade_tipo_pista.png")\
"""))

cells.append(code("""\
barras_100pct(df, "tracado_via_norm",
              "Gravidade por traçado da via (% de acidentes)",
              "fig14_gravidade_tracado.png")\
"""))

cells.append(code("""\
barras_100pct(df, "uso_solo",
              "Gravidade por uso do solo: Sim = urbano, Nao = rural (% de acidentes)",
              "fig15_gravidade_uso_solo.png")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: nas barras acima, identifique qual categoria de cada variável tem a maior \
barra vermelha (% fatais). Existe algum resultado surpreendente? Por exemplo, \
pista simples é mais letal que pista dupla? Por quê isso faz sentido (ou nao)?
>
> Sugestão: pista simples tende a ter maior % de fatais que pista dupla, pois permite \
colisoes frontais com veículos em sentido contrário. Traçado em curva e declive tendem \
a aparecer entre os mais letais. Área rural (uso_solo = Nao) claramente mais letal que urbana.\
"""))

# 6.2 Letalidade por tipo de acidente e macrocausa
cells.append(md("""\
### 6.2 Índice de letalidade por tipo de acidente e macrocausa

Mortos por 100 acidentes. Esse índice é preferível ao número absoluto de mortos \
porque corrige pelo volume de cada categoria.\
"""))

cells.append(code("""\
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for ax, var, titulo in [
    (axes[0], "tipo_acidente",  "Letalidade por tipo de acidente\\n(mortos por 100 acidentes)"),
    (axes[1], "macrocausa",     "Letalidade por macrocausa\\n(mortos por 100 acidentes)"),
]:
    let = indice_letalidade(df.dropna(subset=[var]), var)
    let = let.head(12)  # top 12
    ax.barh(let[var][::-1], let["letalidade_por_100"][::-1], color="#f44336")
    ax.set_xlabel("Mortos por 100 acidentes")
    ax.set_title(titulo)
    for i, (v, n) in enumerate(zip(let["letalidade_por_100"][::-1], let["n_acidentes"][::-1])):
        ax.text(v + 0.05, i, f"n={n}", va="center", fontsize=7.5, color="gray")

fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig16_letalidade_tipo_macrocausa.png")
plt.show()
print("fig16 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: compare o tipo de acidente mais frequente com o mais letal. O fato de colisão \
traseira ser comum nao significa que seja perigosa por acidente. Qual macrocausa, apesar \
de rara, tem letalidade muito acima da média?
>
> Sugestão: colisão frontal e atropelamento costumam liderar a letalidade. \
Álcool ou substancias e fator externo costumam ter letalidade alta apesar de volume menor. \
Isso reforça a importância de políticas de fiscalização de alcoolemia e de rodovias de acesso rural.\
"""))

# 6.3 Heatmap dia × hora
cells.append(md("""\
### 6.3 Heatmap dia da semana x hora: volume e letalidade

Dois heatmaps: total de acidentes (volume) e letalidade (mortos por 100 acidentes). \
Comparar os dois revela se os horários mais movimentados são também os mais perigosos, \
ou se existem horários com poucos acidentes mas alta letalidade.\
"""))

cells.append(code("""\
ORDEM_DIA = ["segunda-feira", "terça-feira", "quarta-feira",
             "quinta-feira", "sexta-feira", "sábado", "domingo"]
# garante apenas os dias presentes
ordem_valida = [d for d in ORDEM_DIA if d in df["dia_semana"].unique()]

pivot_vol = df.groupby(["dia_semana", "hora"]).size().unstack(fill_value=0)
pivot_vol = pivot_vol.reindex(ordem_valida)

pivot_let = (
    df.groupby(["dia_semana", "hora"])
    .agg(n=("id", "count"), mortos=("mortos", "sum"))
    .assign(letalidade=lambda x: x["mortos"] / x["n"] * 100)
    ["letalidade"]
    .unstack(fill_value=0)
    .reindex(ordem_valida)
)

fig, axes = plt.subplots(2, 1, figsize=(14, 9))

sns.heatmap(pivot_vol, cmap="YlOrRd", ax=axes[0], linewidths=0.3,
            cbar_kws={"label": "N. de acidentes"})
axes[0].set_title("Volume de acidentes por dia da semana e hora")
axes[0].set_xlabel("Hora do dia")
axes[0].set_ylabel("Dia da semana")

sns.heatmap(pivot_let, cmap="Reds", ax=axes[1], linewidths=0.3,
            cbar_kws={"label": "Mortos por 100 acidentes"})
axes[1].set_title("Letalidade por dia da semana e hora (mortos por 100 acidentes)")
axes[1].set_xlabel("Hora do dia")
axes[1].set_ylabel("Dia da semana")

fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig17_heatmap_dia_hora.png")
plt.show()
print("fig17 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: compare os dois heatmaps. O pico de volume (horário de rush) coincide com o \
pico de letalidade? Madrugada de sábado e domingo costuma ter volume baixo, mas \
é o período de maior letalidade na maioria das rodovias. Isso tem explicação?
>
> Sugestão: o pico de volume tende a estar nos horários de rush (6-9h e 17-19h) \
em dias úteis. O pico de letalidade tende a estar na madrugada de sexta para \
sábado e sábado para domingo (0-4h), associado a condução sob influência de álcool \
e maior velocidade. Isso justifica fiscalização diferenciada nesses períodos.\
"""))

# 6.4 Comparação SC x PR x RS
cells.append(md("""\
### 6.4 Comparação entre estados (SC, PR, RS) normalizada

Comparamos as três UFs pela distribuição percentual de gravidade e pelo índice de letalidade. \
Como cada estado tem volume diferente de acidentes, usamos taxas e nao contagens absolutas.\
"""))

cells.append(code("""\
# Distribuição de gravidade por UF
tabela_uf = pd.crosstab(df["uf"], df["classificacao_acidente"], normalize="index") * 100
tabela_uf = tabela_uf[ORDEM_GRAVIDADE]

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Barras empilhadas 100%
tabela_uf_plot = tabela_uf.sort_values("Com Vítimas Fatais")
esq = np.zeros(len(tabela_uf_plot))
for classe in ORDEM_GRAVIDADE:
    vals = tabela_uf_plot[classe].values
    axes[0].barh(tabela_uf_plot.index, vals, left=esq,
                 color=CORES_GRAVIDADE[classe], label=classe)
    for i, v in enumerate(vals):
        if v > 5:
            axes[0].text(esq[i] + v / 2, i, f"{v:.1f}%",
                         ha="center", va="center", fontsize=8,
                         color="white", fontweight="bold")
    esq += vals
axes[0].set_xlim(0, 100)
axes[0].set_xlabel("Percentual (%)")
axes[0].set_title("Distribuição de gravidade por UF (%)")
axes[0].legend(loc="lower right", fontsize=8)

# Letalidade
let_uf = indice_letalidade(df, "uf").sort_values("letalidade_por_100")
axes[1].barh(let_uf["uf"], let_uf["letalidade_por_100"], color="#f44336")
axes[1].set_xlabel("Mortos por 100 acidentes")
axes[1].set_title("Índice de letalidade por UF")
for i, (v, n) in enumerate(zip(let_uf["letalidade_por_100"], let_uf["n_acidentes"])):
    axes[1].text(v + 0.05, i, f"n={n}", va="center", fontsize=8, color="gray")

fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig18_gravidade_uf.png")
plt.show()
print("fig18 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: algum estado tem letalidade significativamente maior? Lembre que nao temos \
dado de volume de tráfego, entao nao podemos afirmar que um estado é "mais perigoso", \
apenas que seus acidentes registrados tendem a ser mais ou menos graves.
>
> Sugestão: se RS tiver menor volume de acidentes mas letalidade similar ou maior, \
pode indicar que acidentes no RS tendem a ser em trechos mais críticos ou horários \
mais perigosos. Mencionar a limitação de ausência de dados de volume de tráfego.\
"""))

# 6.5 Mapa de pontos
cells.append(md("""\
### 6.5 Mapa de pontos: acidentes fatais destacados

Visualiza a dispersão geográfica dos acidentes na Região Sul. \
Acidentes fatais são destacados em vermelho.\
"""))

cells.append(code("""\
df_geo = df.dropna(subset=["latitude", "longitude"])
df_fatal  = df_geo[df_geo["classificacao_acidente"] == "Com Vítimas Fatais"]
df_ferido = df_geo[df_geo["classificacao_acidente"] == "Com Vítimas Feridas"]
df_semvit = df_geo[df_geo["classificacao_acidente"] == "Sem Vítimas"]

fig, ax = plt.subplots(figsize=(8, 9))
ax.scatter(df_semvit["longitude"], df_semvit["latitude"],
           s=2, alpha=0.25, color="#4caf50", label="Sem Vítimas", rasterized=True)
ax.scatter(df_ferido["longitude"], df_ferido["latitude"],
           s=2, alpha=0.3, color="#ff9800", label="Com Feridos", rasterized=True)
ax.scatter(df_fatal["longitude"], df_fatal["latitude"],
           s=8, alpha=0.7, color="#f44336", label="Com Vítimas Fatais", rasterized=True)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_title(
    f"Distribuição geográfica dos acidentes: Região Sul (jan-mai 2026)\\n"
    f"Fatais destacados em vermelho (n={len(df_fatal):,})"
)
ax.legend(markerscale=3, fontsize=9)
fig.tight_layout()
fig.savefig(f"{FIGURAS}/fig19_mapa_fatais.png")
plt.show()
print("fig19 salva.")\
"""))

cells.append(md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
> Dica: identifique visualmente se os fatais se concentram em determinadas \
regiões ou rodovias. Há trechos com aglomerado denso de pontos vermelhos? \
Isso pode indicar trechos críticos para fiscalização e engenharia de tráfego.
>
> Sugestão: espera-se que fatais se concentrem em rodovias com maior fluxo \
e trechos rurais de pista simples. Aglomerações próximas a divisas estaduais \
ou serras podem indicar trechos críticos conhecidos da BR-116, BR-101 e BR-282.\
"""))

# ── RESUMO FINAL ──────────────────────────────────────────────────────────────
cells.append(md("""\
## 7. Resumo: o que este notebook produziu

- **Tabela de ranking V de Cramér** com todas as variáveis explicativas
- **Tabelas de contingência** com % na linha e letalidade para 6 variáveis
- **12 figuras** salvas em `reports/figuras/` (fig09 a fig19)
- **Alertas metodológicos** incluídos em cada visualização

**Próximos passos:** notebook 04 (modelo de classificação) e notebook 05 (preparação para BI).\
"""))

cells.append(md("""\
---
## Descobertas da equipe (para a AV1)

Liste abaixo as **3 a 5 principais descobertas** deste notebook. \
Cada descoberta deve ter: o fato observado, a variável envolvida e uma \
recomendação ou hipótese para a PRF/DNIT.

> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher)
>
> Exemplo de estrutura:
> 1. **[Variável]:** [o que foi observado]. Recomendação: [ação para PRF/DNIT].
> 2. ...
>
> Lembrete: toda afirmação deve ser acompanhada de: "lembrando que nao há dados \
de volume de tráfego, nao é possível afirmar que X é mais perigoso, apenas que \
os acidentes registrados em X tendem a ser mais graves."\
"""))

# ── MONTAR E SALVAR ───────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "cells": cells
}

out = "notebooks/03_eda_integrada_correlacao.ipynb"
os.makedirs("notebooks", exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook salvo em {out}")
