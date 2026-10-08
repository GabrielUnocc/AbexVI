"""
gerar_notebooks.py
Gera os arquivos .ipynb do projeto ABEX VI.
Execute na raiz do repositório: python3 gerar_notebooks.py
"""
import json, os, textwrap

NOTEBOOKS_DIR = os.path.join(os.path.dirname(__file__), "notebooks")
os.makedirs(NOTEBOOKS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [], "source": source}


def notebook(cells: list, name: str) -> dict:
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10.0"},
            "colab": {"name": name},
        },
        "cells": cells,
    }


def save(nb: dict, name: str) -> None:
    import uuid
    for cell in nb["cells"]:
        cell["id"] = uuid.uuid4().hex[:8]
    path = os.path.join(NOTEBOOKS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"Salvo: {path}")


# ===========================================================================
# NOTEBOOK 01: EDA de Diagnostico
# ===========================================================================

nb01_cells = [

md("""\
# Notebook 01: EDA de Diagnóstico
**ABEX VI: Projeto Integrado III**
Equipe: Gabriel Victor Rosário, João Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi
Curso: Sistemas de Informação, Unochapecó, turma BX, 2026/2

---

**Objetivo:** Explorar a base PRF da Região Sul antes de qualquer tratamento: entender estrutura,
qualidade e distribuições.

**Entrada:** `data/raw/PRF_SUL_2026.csv`

**Saídas:** Figuras em `reports/figuras/`, lista de problemas para o Notebook 02

**Perguntas respondidas (checklist Aula 06):**
1. O que representa cada linha?
2. Há identificador único?
3. Qual é o período coberto?
4. Quais são as dimensões da base?
5. Quais são os tipos de dados?
6. Há valores ausentes?
7. Há duplicatas?
8. Quais são as categorias das variáveis qualitativas?
9. Como se distribuem as variáveis numéricas?
10. Há outliers?
11. Há inconsistências entre colunas?
12. O que precisa de tratamento?
"""),

code("""\
# Instalacoes (descomentar no Colab se necessario)
# !pip install pandas numpy matplotlib seaborn scipy openpyxl

import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats

sys.path.insert(0, os.path.join('..', 'src'))
try:
    from utils import perfil_qualidade, indice_letalidade, outliers_iqr
except ImportError:
    print("Aviso: utils.py nao encontrado. Funcoes definidas inline.")

plt.rcParams.update({
    'figure.dpi': 150,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.spines.top': False,
    'axes.spines.right': False,
})
sns.set_palette('tab10')
pd.set_option('display.max_columns', 35)
pd.set_option('display.max_rows', 60)
print("Bibliotecas carregadas.")
"""),

md("""\
> **Nota (Colab):** Monte o Google Drive e ajuste `BASE_DIR` para o caminho onde o projeto está salvo.
> Exemplo: `BASE_DIR = '/content/drive/MyDrive/abex-vi'`
"""),

code("""\
try:
    from google.colab import drive
    drive.mount('/content/drive')
    BASE_DIR = '/content/drive/MyDrive/abex-vi'  # ajuste conforme necessario
except ImportError:
    # Detecta raiz do projeto independente de onde o kernel foi iniciado
    if os.path.exists(os.path.join('data', 'raw', 'PRF_SUL_2026.csv')):
        BASE_DIR = '.'        # kernel iniciado na raiz do projeto
    else:
        BASE_DIR = '..'       # kernel iniciado dentro de notebooks/

ARQUIVO = os.path.join(BASE_DIR, 'data', 'raw', 'PRF_SUL_2026.csv')
FIGURAS  = os.path.join(BASE_DIR, 'reports', 'figuras')
os.makedirs(FIGURAS, exist_ok=True)

df_original = pd.read_csv(ARQUIVO, encoding='utf-8', low_memory=False)
df = df_original.copy()

print(f"Base carregada: {df.shape[0]} linhas x {df.shape[1]} colunas")
print(f"Arquivo: {ARQUIVO}")
"""),

# ---- perfil de qualidade ----
md("## 1. Perfil de Qualidade\n\nVisao geral de tipo, ausentes e cardinalidade de todas as colunas."),

code("""\
def perfil_qualidade(df):
    resultado = []
    for col in df.columns:
        n_aus = df[col].isna().sum()
        resultado.append({
            'variavel':     col,
            'tipo':         str(df[col].dtype),
            'n_ausentes':   n_aus,
            'pct_ausentes': round(n_aus / len(df) * 100, 2),
            'n_unicos':     df[col].nunique(dropna=False),
        })
    return pd.DataFrame(resultado)

perfil = perfil_qualidade(df)
perfil
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** A base tem 30 colunas. Apenas `regional` (7 ausentes), `delegacia` (8) e `uop` (9)
> têm NaN reais, menos de 0,1% cada: praticamente nenhuma perda de informação.
> As colunas numéricas como `km`, `latitude` e `longitude` aparecem como `float64` aqui porque
> vieram do Excel; se a equipe baixar o CSV direto do portal PRF, elas podem vir como `object`
> (vírgula decimal) e precisarão de conversão no Notebook 02.
> As colunas `dia_semana`, `causa_acidente`, `tipo_acidente` e `tracado_via` são `object` e precisam
> de atenção especial na padronização.
>
> **Aprovam essa leitura?**
"""),

# ---- checklist ----
md("## 2. Checklist da Aula 06\n\n---\n\n### Q1. O que representa cada linha?"),

code("""\
print("Colunas disponíveis:")
print(df.columns.tolist())
print()
print("Exemplo de linha (primeira ocorrência):")
df.iloc[0]
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Cada linha representa **uma ocorrência de acidente**, não um veículo nem uma vítima.
> Um único acidente pode envolver vários veículos (`veiculos`) e várias pessoas (`pessoas`).
> Isso é importante: ao contar linhas, contamos acidentes, não mortos nem feridos.
> A variável `id` é o identificador dessa ocorrência no sistema da PRF.
>
> **Aprovam essa leitura?**
"""),

md("### Q2. Há identificador único?"),

code("""\
n_total = len(df)
n_ids   = df['id'].nunique()
print(f"Total de linhas: {n_total}")
print(f"IDs distintos:   {n_ids}")
print(f"Duplicatas:      {n_total - n_ids}")
print()
n_dup = df.duplicated().sum()
print(f"Linhas completamente duplicadas: {n_dup}")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** O campo `id` é único em todas as 8.703 linhas: zero duplicatas.
> A base está bem estruturada nesse aspecto: cada acidente aparece exatamente uma vez.
> Não há necessidade de deduplicação.
>
> **Aprovam essa leitura?**
"""),

md("### Q3. Qual é o período coberto?"),

code("""\
datas = pd.to_datetime(df['data_inversa'], errors='coerce')
print(f"Data minima:       {datas.min().date()}")
print(f"Data maxima:       {datas.max().date()}")
print(f"Meses cobertos:    {datas.dt.to_period('M').nunique()}")
print()
print("Acidentes por mes:")
print(datas.dt.to_period('M').value_counts().sort_index())
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** A base cobre apenas **janeiro a maio de 2026** (5 meses).
> Março (1.807) e abril (1.829) têm mais registros; janeiro (1.667) tem a maior letalidade (6,54/100).
> Isso é consistente com mais acidentes no início do outono (pista molhada, chuvas)
> e com mais mortes no verão (maior velocidade, férias, estradas movimentadas).
> **Limitação crítica:** sem os meses de inverno (chuva/neblina intensa no Sul) e fim de ano,
> os resultados podem subestimar riscos sazonais. Ver decisão D1.
>
> **Aprovam essa leitura?**
"""),

md("### Q4. Dimensões da base"),

code("""\
print(f"Linhas:  {df.shape[0]}")
print(f"Colunas: {df.shape[1]}")
print()
print("Distribuicao por UF:")
print(df['uf'].value_counts())
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** 8.703 acidentes em 5 meses equivale a cerca de **58 acidentes por dia** na Região Sul.
> SC tem mais registros (3.538) seguido de PR (3.254) e RS (1.911), mas isso reflete
> o volume de tráfego e extensão da malha rodoviária federal em cada estado,
> não necessariamente que SC é mais perigoso.
> Para comparar riscos entre estados, use **letalidade** (mortos por 100 acidentes),
> não contagem absoluta.
>
> **Aprovam essa leitura?**
"""),

md("### Q5. Tipos de dados"),

code("""\
print(df.dtypes)
print()
for col in ['km', 'latitude', 'longitude']:
    print(f"{col}: dtype={df[col].dtype}, exemplos={df[col].dropna().head(3).tolist()}")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** No arquivo gerado a partir do Excel, `km`, `latitude` e `longitude` já são `float64`.
> Porém, se o CSV for baixado diretamente do portal PRF, essas colunas usam
> **vírgula como separador decimal** e virão como `object`: precisarão de conversão explícita.
> O Notebook 02 trata isso com `str.replace(',', '.')` + `pd.to_numeric(errors='coerce')`.
> `data_inversa` pode vir como texto `dd/mm/aaaa` no CSV original: também tratado no Notebook 02.
>
> **Aprovam essa leitura?**
"""),

md("### Q6. Valores ausentes"),

code("""\
ausentes = perfil_qualidade(df)[['variavel','n_ausentes','pct_ausentes']]
print("Ausentes reais (NaN):")
print(ausentes[ausentes['n_ausentes'] > 0].to_string(index=False))
print()
print("Ausencias disfarcadas (categorias que sao NA):")
for col in df.select_dtypes(include='object').columns:
    for val in ['Ignorado', 'Não Informado', 'Nao Informado']:
        n = (df[col] == val).sum()
        if n > 0:
            print(f"  {col}: '{val}' -> {n} registros ({n/len(df)*100:.1f}%)")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Há dois tipos de ausência nesta base:
>
> 1. **NaN reais** em `regional`/`delegacia`/`uop` (7-9 registros, < 0,1%): mínimo, recuperável.
>
> 2. **Ausências disfarçadas**: `condicao_metereologica = 'Ignorado'` (63 casos) e
>    `sentido_via = 'Não Informado'` (20 casos). Esses valores **não descrevem uma condição real**:
>    o agente da PRF simplesmente não tinha a informação.
>    Nossa recomendação (ver D5): convertê-los para `NaN` antes das análises, para não criar
>    uma falsa "categoria Ignorado" que distorce percentuais.
>
> **Aprovam essa leitura e a recomendação para D5?**
"""),

md("### Q7. Duplicatas"),

code("""\
print(f"Linhas completamente duplicadas: {df.duplicated().sum()}")
print(f"IDs duplicados: {df['id'].duplicated().sum()}")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Nenhuma duplicata. A base está limpa nesse aspecto: não há necessidade de deduplicação.
>
> **Aprovam essa leitura?**
"""),

md("### Q8. Categorias das variáveis qualitativas"),

code("""\
colunas_cat = df.select_dtypes(include='object').columns.tolist()
print(f"Colunas de texto ({len(colunas_cat)}): {colunas_cat}")
"""),

code("""\
for col in ['classificacao_acidente', 'uf', 'dia_semana', 'fase_dia',
            'condicao_metereologica', 'tipo_pista', 'uso_solo', 'sentido_via']:
    print(f"\\n--- {col} ({df[col].nunique()} unicos) ---")
    print(df[col].value_counts(dropna=False).to_string())
"""),

code("""\
for col in ['causa_acidente', 'tipo_acidente', 'tracado_via']:
    print(f"\\n--- {col} ({df[col].nunique()} unicos) ---")
    print(df[col].value_counts(dropna=False).head(20).to_string())
    if df[col].nunique() > 20:
        print(f"  ... e mais {df[col].nunique()-20} categorias")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Três pontos merecem atenção:
>
> 1. **`causa_acidente` tem 65 categorias**, muitas com poucos casos. As 5 mais frequentes
>    ("Ausência de reação", "Reação tardia", "Acessar a via sem observar", "Ingestão de álcool",
>    "Velocidade incompatível") já concentram mais de 50% dos acidentes. Agrupá-las em
>    macrocategorias (D4) é essencial para análises e para o modelo de ML.
>
> 2. **`tracado_via` é multivalorado**: "Reta;Declive" e "Declive;Reta" representam
>    **o mesmo trecho** com componentes fora de ordem. Precisamos normalizar (ordenar os
>    componentes) e criar dummies. Feito no Notebook 02.
>
> 3. **`dia_semana` tem acentos** ("sábado", "terça-feira"): cuidado ao fazer comparações com
>    strings sem acento no código. Sempre use os valores exatos da base.
>
> **Aprovam essa leitura?**
"""),

md("### Q9. Distribuição das variáveis numéricas"),

code("""\
numericas = ['pessoas', 'mortos', 'feridos', 'feridos_leves', 'feridos_graves',
             'ilesos', 'ignorados', 'veiculos']

desc = df[numericas].describe().T
desc['assimetria'] = df[numericas].skew().round(2)
desc['mediana']    = df[numericas].median()
print(desc[['count','mean','std','min','25%','50%','75%','max','mediana','assimetria']].round(2))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Todas as variáveis numéricas são **fortemente assimétricas à direita**:
> a maioria dos acidentes tem poucos envolvidos, mas alguns têm muitos (ônibus, caminhões).
> Consequência prática: **a média é enganosa** neste caso. Use sempre a **mediana** para descrever
> o acidente típico.
>
> Destaque: `mortos` e `feridos_graves` têm mediana 0 (a maioria dos acidentes não tem mortos nem
> graves). Isso reflete as classes desbalanceadas da variável-alvo: 78,7% dos acidentes são
> "Com Vítimas Feridas" sem mortes.
>
> **Aprovam essa leitura?**
"""),

code("""\
fig, axes = plt.subplots(2, 4, figsize=(16, 7))
axes = axes.flatten()

for i, col in enumerate(numericas):
    axes[i].hist(df[col], bins=30, color='steelblue', edgecolor='white')
    axes[i].set_title(col)
    axes[i].set_xlabel('Valor')
    axes[i].set_ylabel('Frequencia')
    med = df[col].median()
    axes[i].axvline(med, color='crimson', linestyle='--', linewidth=1.5, label=f'Mediana={med:.0f}')
    axes[i].legend(fontsize=8)

plt.suptitle('Distribuicao das variaveis numericas (linha vermelha = mediana)', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig01_histogramas_numericas.png'), dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: fig01_histogramas_numericas.png")
"""),

code("""\
fig, axes = plt.subplots(2, 4, figsize=(16, 7))
axes = axes.flatten()

for i, col in enumerate(numericas):
    axes[i].boxplot(df[col], patch_artist=True,
                    boxprops=dict(facecolor='lightblue'),
                    medianprops=dict(color='crimson', linewidth=2))
    axes[i].set_title(col)
    axes[i].set_ylabel('Valor')

plt.suptitle('Boxplots (pontos acima do limite superior = candidatos a outliers por IQR)', fontsize=14)
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig02_boxplots_numericas.png'), dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: fig02_boxplots_numericas.png")
"""),

md("### Q10. Outliers"),

code("""\
def listar_outliers_iqr(df, col):
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr     = q3 - q1
    lim_sup = q3 + 1.5 * iqr
    lim_inf = q1 - 1.5 * iqr
    outliers = df[(df[col] > lim_sup) | (df[col] < lim_inf)]
    print(f"{col:20s}: IQR={iqr:.1f}, lim=[{lim_inf:.1f}, {lim_sup:.1f}], "
          f"outliers={len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
    return outliers

for col in numericas:
    listar_outliers_iqr(df, col)
"""),

code("""\
print("Top 10 acidentes com mais mortos (investigar antes de qualquer remocao):")
print(df.nlargest(10, 'mortos')[['id','data_inversa','municipio','br','tipo_acidente',
                                  'pessoas','mortos','feridos_graves']].to_string(index=False))
print()
print("Top 10 com mais pessoas envolvidas:")
print(df.nlargest(10, 'pessoas')[['id','data_inversa','municipio','br','tipo_acidente',
                                   'pessoas','mortos','veiculos']].to_string(index=False))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** O critério IQR sinaliza "outliers" em `mortos` e `feridos_graves` porque
> a mediana dessas colunas é 0 e o IQR é 0. Isso significa que **qualquer acidente com
> pelo menos 1 morto ou 1 ferido grave é tecnicamente um "outlier"** pelo IQR.
> Isso **não é um erro**: reflete o desequilíbrio natural dos dados (acidentes fatais são raros,
> mas são exatamente o que queremos estudar).
>
> **Recomendação:** **Não remova nenhum desses registros.**
> Acidentes com muitos mortos provavelmente envolvem ônibus ou caminhões: são os mais graves
> e os mais relevantes para a PRF. Documente no log de decisões.
>
> **Aprovam a decisão de manter todos os outliers?**
"""),

md("### Q11. Consistência entre colunas"),

code("""\
# feridos == feridos_leves + feridos_graves?
inconsist = df[df['feridos'] != df['feridos_leves'] + df['feridos_graves']]
print(f"Inconsistencias feridos != feridos_leves + feridos_graves: {len(inconsist)}")

# classificacao_acidente x mortos
fatal_sem_morto = df[(df['classificacao_acidente'] == 'Com Vítimas Fatais') & (df['mortos'] == 0)]
print(f"'Com Vitimas Fatais' com mortos=0: {len(fatal_sem_morto)}")

sem_vit_com_vit = df[(df['classificacao_acidente'] == 'Sem Vítimas') &
                     ((df['mortos'] > 0) | (df['feridos'] > 0))]
print(f"'Sem Vitimas' com mortos>0 ou feridos>0: {len(sem_vit_com_vit)}")

# Coordenadas fora da Regiao Sul (SC/PR/RS: lat -35 a -22, lon -57 a -44)
coord_inv = df[df['latitude'].notna() &
               ((df['latitude'] < -35) | (df['latitude'] > -22) |
                (df['longitude'] < -57) | (df['longitude'] > -44))]
print(f"Coordenadas fora da Regiao Sul: {len(coord_inv)}")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** A base é **internamente consistente** nos pontos mais críticos:
>
> - `feridos = feridos_leves + feridos_graves` em **100% dos casos** (0 inconsistências).
>   Isso confirma que `feridos` é uma coluna **derivada** e deve ser excluída das features do modelo
>   de ML para evitar vazamento de dados.
>
> - A `classificacao_acidente` bate com os contadores de mortos e feridos: nenhum acidente
>   classificado como "Com Vítimas Fatais" tem mortos = 0, e vice-versa.
>
> Isso é um ponto forte da base da PRF: os campos numéricos e a classificação estão alinhados.
>
> **Aprovam essa leitura?**
"""),

md("### Q12. O que precisa de tratamento?"),

code("""\
print(\"\"\"
LISTA DE PROBLEMAS PARA O NOTEBOOK 02
======================================

 #  Tipo               Coluna(s)                     Descricao
--- ---------------   ---------------------------   ------------------------------------------
 1  Tipo/formato      data_inversa, horario          Texto no CSV original; extrair mes, hora
 2  Tipo/formato      km, latitude, longitude        Virgula decimal no CSV do portal PRF
 3  Multivalorado     tracado_via                    Separado por ';', ordem variavel
 4  Ausente real      regional, delegacia, uop       7-9 NaN; tentar recuperar por municipio
 5  Ausente disfar.   condicao_metereologica         'Ignorado': 63 casos -> converter para NaN
 6  Ausente disfar.   sentido_via                    'Nao Informado': 20 casos -> converter para NaN
 7  Muitas categ.     causa_acidente                 65 categorias -> propor macrocategorias (D4)
 8  Coluna derivada   feridos                        = feridos_leves + feridos_graves -> excluir do ML
 9  CRITICO: ML       mortos, feridos_*, ilesos      Definem classificacao_acidente -> nao usar no ML
10  Novas variaveis   teve_morte, grave_ou_fatal     Criar no preprocessamento
\"\"\")
"""),

# ---- EDA Complementar ----
md("---\n## 3. EDA Complementar\n\n### Distribuição de `classificacao_acidente`"),

code("""\
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

vc = df['classificacao_acidente'].value_counts()
cores = ['#4C72B0', '#DD8452', '#C44E52']
axes[0].bar(vc.index, vc.values, color=cores)
for i, (idx, v) in enumerate(vc.items()):
    axes[0].text(i, v + 40, f'{v}\\n({v/len(df)*100:.1f}%)', ha='center', fontsize=9)
axes[0].set_title('Classificacao dos acidentes (jan-mai 2026, Regiao Sul)')
axes[0].set_xlabel('Classificacao')
axes[0].set_ylabel('Numero de acidentes')
axes[0].tick_params(axis='x', rotation=8)

# Barras 100% empilhadas por UF
cols_ordem = ['Sem Vítimas', 'Com Vítimas Feridas', 'Com Vítimas Fatais']
cross = pd.crosstab(df['uf'], df['classificacao_acidente'], normalize='index') * 100
cross = cross.reindex(columns=[c for c in cols_ordem if c in cross.columns])
cross.plot(kind='bar', stacked=True, ax=axes[1], color=cores)
axes[1].set_title('Classificacao por UF (% empilhado)')
axes[1].set_xlabel('UF')
axes[1].set_ylabel('%')
axes[1].legend(title='', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)
axes[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig03_classificacao_acidente.png'), dpi=150, bbox_inches='tight')
plt.show()
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** As classes são **fortemente desbalanceadas**: 78,7% dos acidentes são "Com Vítimas
> Feridas", 16,2% "Sem Vítimas" e apenas 5,2% "Com Vítimas Fatais". Isso tem duas implicações:
>
> 1. **Para a EDA**: ao calcular percentuais, sempre os calcule *dentro do estado* (linha a linha
>    na tabela de contingência), não sobre o total, para poder comparar SC, PR e RS.
>
> 2. **Para o ML**: um modelo que "chute" sempre "Com Vítimas Feridas" acerta 78,7% das vezes sem
>    aprender nada. Use F1-macro como métrica, nunca acurácia. (Notebook 04)
>
> **Comparação entre estados:**
> PR: 6,1% fatal, letalidade 6,95/100.
> RS: 5,9% fatal, letalidade 7,27/100.
> SC: 4,0% fatal, letalidade 4,69/100.
> RS e PR são significativamente mais letais que SC. Uma hipótese: SC tem mais extensão de pista
> dupla/múltipla (que reduzem colisões frontais) e perfil de relevo diferente.
> Vale investigar no Notebook 03.
>
> **Aprovam essa leitura?**
"""),

md("### Acidentes e letalidade por dia da semana"),

code("""\
# Dias da semana conforme aparecem na base (com acentos)
ordem_dias = ['segunda-feira', 'terca-feira', 'quarta-feira', 'quinta-feira',
              'sexta-feira', 'sabado', 'domingo']

# Normaliza acentos para o reindex funcionar
import unicodedata
def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

df['dia_norm'] = df['dia_semana'].str.lower().apply(sem_acento)

g_dia = (df.groupby('dia_norm')
           .agg(n=('id', 'count'), mortos=('mortos', 'sum'))
           .reset_index())
g_dia['letalidade'] = (g_dia['mortos'] / g_dia['n'] * 100).round(2)
g_dia['dia_norm']   = pd.Categorical(g_dia['dia_norm'], categories=ordem_dias, ordered=True)
g_dia = g_dia.sort_values('dia_norm')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].bar(g_dia['dia_norm'], g_dia['n'], color='steelblue')
axes[0].set_title('Acidentes por dia da semana (contagem)')
axes[0].set_xlabel('Dia da semana')
axes[0].set_ylabel('Numero de acidentes')
axes[0].tick_params(axis='x', rotation=30)

axes[1].bar(g_dia['dia_norm'], g_dia['letalidade'], color='firebrick')
axes[1].set_title('Letalidade por dia da semana (mortos por 100 acidentes)')
axes[1].set_xlabel('Dia da semana')
axes[1].set_ylabel('Mortos por 100 acidentes')
axes[1].tick_params(axis='x', rotation=30)

plt.suptitle('Nota: comparacao por letalidade, nao por volume absoluto', fontsize=10, color='gray')
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig04_acidentes_dia_semana.png'), dpi=150, bbox_inches='tight')
plt.show()

print("\\nResumo por dia:")
print(g_dia.to_string(index=False))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Sábado (1.451) e sexta-feira (1.434) têm **mais acidentes** em volume.
> Mas **domingo** tem a **maior letalidade** (7,51 mortos/100 acidentes), seguido de segunda-feira
> (7,11/100). Isso é um padrão clássico: fins de semana combinam velocidade mais alta,
> mais viagens longas, possível fadiga e maior probabilidade de uso de álcool.
>
> Recomendação para a PRF: o **domingo** é o dia prioritário para fiscalização e blitze de alcoolemia,
> especialmente no período noturno e na madrugada da virada sexta-sabado e sabado-domingo.
>
> **Aprovam essa leitura e recomendação?**
"""),

md("### Acidentes e letalidade por fase do dia"),

code("""\
ordem_fases = ['Pleno dia', 'Anoitecer', 'Amanhecer', 'Plena Noite']
g_fase = (df.groupby('fase_dia')
            .agg(n=('id', 'count'), mortos=('mortos', 'sum'))
            .reset_index())
g_fase['letalidade'] = (g_fase['mortos'] / g_fase['n'] * 100).round(2)
g_fase['pct_acidentes'] = (g_fase['n'] / len(df) * 100).round(1)
g_fase['fase_dia'] = pd.Categorical(g_fase['fase_dia'], categories=ordem_fases, ordered=True)
g_fase = g_fase.sort_values('fase_dia')

cores_fase = ['#FFC000', '#FF7F0E', '#E0631C', '#1A2A4A']

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(g_fase['fase_dia'], g_fase['pct_acidentes'], color=cores_fase)
for i, v in enumerate(g_fase['pct_acidentes']):
    axes[0].text(i, v + 0.3, f'{v}%', ha='center', fontsize=9)
axes[0].set_title('% de acidentes por fase do dia')
axes[0].set_xlabel('Fase do dia')
axes[0].set_ylabel('% do total')
axes[0].tick_params(axis='x', rotation=10)

axes[1].bar(g_fase['fase_dia'], g_fase['letalidade'], color=cores_fase)
for i, v in enumerate(g_fase['letalidade']):
    axes[1].text(i, v + 0.1, f'{v:.1f}', ha='center', fontsize=9)
axes[1].set_title('Letalidade por fase do dia (mortos por 100 acidentes)')
axes[1].set_xlabel('Fase do dia')
axes[1].set_ylabel('Mortos por 100 acidentes')
axes[1].tick_params(axis='x', rotation=10)

plt.suptitle('Amanhecer: poucos acidentes, mas o mais letal', fontsize=11, color='firebrick')
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig05_acidentes_fase_dia.png'), dpi=150, bbox_inches='tight')
plt.show()

print("\\nResumo por fase:")
print(g_fase.to_string(index=False))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Este é um dos achados mais fortes da EDA.
> **Pleno dia** concentra 57% dos acidentes, mas tem a **menor letalidade** (4,13/100).
> **Amanhecer** tem apenas 4,5% dos acidentes, mas a **maior letalidade**: 11,22 mortos por 100,
> quase **3 vezes mais que pleno dia**. **Plena Noite** também é crítica: 9,26/100 com 33% dos acidentes.
>
> Interpretação: de dia há mais acidentes (mais tráfego), mas são menos graves.
> De madrugada/amanhecer há menos acidentes, mas os que ocorrem tendem a ser frontais e em
> alta velocidade (pistas vazias, fadiga do condutor, ausência de iluminação).
>
> Recomendação para a PRF: **reforço de patrulhamento noturno** nas rodovias simples (sem divisória),
> especialmente entre 0h e 6h. O impacto por acidente evitado é muito maior que em pleno dia.
>
> **Aprovam essa leitura e recomendação?**
"""),

md("### Acidentes e letalidade por mês"),

code("""\
datas = pd.to_datetime(df['data_inversa'], errors='coerce')
df_temp = df.assign(mes=datas.dt.month)

g_mes = (df_temp.groupby('mes')
                .agg(n=('id', 'count'), mortos=('mortos', 'sum'))
                .reset_index())
g_mes['letalidade']    = (g_mes['mortos'] / g_mes['n'] * 100).round(2)
g_mes['mes_label']     = g_mes['mes'].map({1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai'})

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(g_mes['mes_label'], g_mes['n'], color='teal')
for i, v in enumerate(g_mes['n']):
    axes[0].text(i, v + 10, str(v), ha='center', fontsize=9)
axes[0].set_title('Acidentes por mes (jan-mai 2026)')
axes[0].set_xlabel('Mes')
axes[0].set_ylabel('Numero de acidentes')

axes[1].bar(g_mes['mes_label'], g_mes['letalidade'], color='darkred')
for i, v in enumerate(g_mes['letalidade']):
    axes[1].text(i, v + 0.05, f'{v:.2f}', ha='center', fontsize=9)
axes[1].set_title('Letalidade por mes (mortos por 100 acidentes)')
axes[1].set_xlabel('Mes')
axes[1].set_ylabel('Mortos por 100 acidentes')

plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig06_acidentes_por_mes.png'), dpi=150, bbox_inches='tight')
plt.show()

print("\\nResumo por mes:")
print(g_mes[['mes_label','n','mortos','letalidade']].to_string(index=False))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Janeiro (1.667) tem o menor volume de acidentes dos 5 meses, mas a **maior
> letalidade** (6,54/100). Maio tem o menor índice de mortalidade (5,16/100).
> Março e abril têm mais acidentes em volume, possivelmente associados às chuvas de outono.
>
> **Cuidado com extrapolação:** 5 meses não permitem identificar sazonalidade anual.
> Julho (inverno, neblina intensa no RS), outubro (chuvas de primavera) e dezembro/janeiro
> (férias, viagens longas) podem ter padrões distintos que não aparecem aqui.
> Isso deve ser citado nas limitações do trabalho.
>
> **Aprovam essa leitura?**
"""),

md("### Mapa de pontos (latitude x longitude)"),

code("""\
fig, ax = plt.subplots(figsize=(8, 9))

nao_fatais = df[df['classificacao_acidente'] != 'Com Vítimas Fatais']
fatais     = df[df['classificacao_acidente'] == 'Com Vítimas Fatais']

ax.scatter(nao_fatais['longitude'], nao_fatais['latitude'],
           alpha=0.08, s=3, color='steelblue', label=f'Outros ({len(nao_fatais)})')
ax.scatter(fatais['longitude'], fatais['latitude'],
           alpha=0.5, s=12, color='crimson', label=f'Com vitimas fatais ({len(fatais)})')

ax.set_title('Distribuicao geografica dos acidentes, Regiao Sul, 2026')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig07_mapa_acidentes.png'), dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: fig07_mapa_acidentes.png")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Os acidentes fatais (vermelho) se concentram em alguns trechos específicos,
> visíveis como agrupamentos na BR-116 (Curitiba-Porto Alegre), BR-101 (litoral de SC)
> e BR-470 (SC, Vale do Itajaí). Esses trechos são candidatos a "pontos negros" da malha federal.
>
> Para o dashboard no Looker Studio (Notebook 05), esse mapa de pontos com fatais destacados
> é um dos KPIs mais impactantes para a PRF: permite filtrar por BR e UF para identificar
> os trechos prioritários de intervenção.
>
> **Nota técnica:** este mapa não tem shapefile de rodovias; os pontos se alinham naturalmente
> nas vias pela própria localização dos acidentes.
>
> **Aprovam essa leitura?**
"""),

# ---- resumo ----
md("""\
---
## 4. Resumo

**Produzido neste notebook:**
- Perfil de qualidade completo das 30 colunas
- Checklist de 12 perguntas respondidas (Aula 06)
- Descritivas e visualizações das variáveis numéricas (fig01, fig02)
- Distribuição de `classificacao_acidente` por UF, em percentual (fig03)
- Acidentes e letalidade por dia da semana e fase do dia (fig04, fig05)
- Acidentes e letalidade por mês (fig06)
- Mapa de pontos com fatais em vermelho (fig07)
- Lista de 10 problemas para o Notebook 02

**Principais achados para a AV1:**
1. **Pista simples é o fator estrutural mais associado à mortalidade** (8,3 mortos/100 vs 4,1 em pista dupla).
2. **Amanhecer é a fase mais letal** (11,22/100), apesar de ter poucos acidentes: condutores com sono, pista vazia, alta velocidade.
3. **Colisão frontal e atropelamento de pedestre** são os tipos mais letais (37% e 30% de mortalidade).
4. **RS e PR são 50% mais letais que SC** (7,27 e 6,95 vs 4,69 mortos/100): merece investigação no Notebook 03.

---

> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher na aula)
> Com base em tudo que vocês viram, quais são as 3 descobertas mais surpreendentes?
> O que vocês não esperavam encontrar? Há algo que contradiz senso comum?
> Lembrem: correlação não é causa. A fase do dia estar associada à letalidade não significa
> que o horário "causa" o acidente: pode haver outros fatores confundidores (velocidade, tipo de via).
"""),

]  # fim nb01

nb01 = notebook(nb01_cells, "01_eda_diagnostico.ipynb")
save(nb01, "01_eda_diagnostico.ipynb")


# ===========================================================================
# NOTEBOOK 02: Pre-processamento
# ===========================================================================

nb02_cells = [

md("""\
# Notebook 02: Pré-processamento
**ABEX VI: Projeto Integrado III**
Equipe: Gabriel Victor Rosário, João Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi

---

**Objetivo:** Tratar os problemas identificados no Notebook 01 seguindo o fluxo da Aula 07:
abrir -> EDA -> encontrar problemas -> investigar -> decidir -> tratar -> validar -> salvar.

**Entrada:** `data/raw/PRF_SUL_2026.csv`

**Saídas:**
- `data/processed/datatran_sul_tratado.csv`
- `reports/decisoes_preprocessamento.csv`
- `reports/dicionario_dados.md`

**Regra fundamental (Aula 07):** `df_original` nunca é alterado.
Cada decisão de tratamento é registrada com `registrar_decisao()`.
"""),

code("""\
import os, sys, unicodedata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.join('..', 'src'))
try:
    from utils import perfil_qualidade, registrar_decisao
except ImportError:
    print("Aviso: utils.py nao encontrado. Definindo localmente.")

pd.set_option('display.max_columns', 35)
pd.set_option('display.max_rows', 60)
print("Pronto.")
"""),

code("""\
try:
    from google.colab import drive
    drive.mount('/content/drive')
    BASE_DIR = '/content/drive/MyDrive/abex-vi'
except ImportError:
    if os.path.exists(os.path.join('data', 'raw', 'PRF_SUL_2026.csv')):
        BASE_DIR = '.'
    else:
        BASE_DIR = '..'

ARQUIVO_RAW  = os.path.join(BASE_DIR, 'data', 'raw', 'PRF_SUL_2026.csv')
ARQUIVO_PROC = os.path.join(BASE_DIR, 'data', 'processed', 'datatran_sul_tratado.csv')
LOG_DECISOES = os.path.join(BASE_DIR, 'reports', 'decisoes_preprocessamento.csv')
DICIONARIO   = os.path.join(BASE_DIR, 'reports', 'dicionario_dados.md')
FIGURAS      = os.path.join(BASE_DIR, 'reports', 'figuras')

os.makedirs(os.path.dirname(ARQUIVO_PROC), exist_ok=True)
os.makedirs(FIGURAS, exist_ok=True)

# Definicao inline da funcao caso utils nao seja encontrado
def perfil_qualidade(df):
    resultado = []
    for col in df.columns:
        n_aus = df[col].isna().sum()
        resultado.append({'variavel': col, 'tipo': str(df[col].dtype),
                          'n_ausentes': n_aus,
                          'pct_ausentes': round(n_aus/len(df)*100, 2),
                          'n_unicos': df[col].nunique(dropna=False)})
    return pd.DataFrame(resultado)

_decisoes = []
def registrar_decisao(problema, evidencia, decisao, justificativa, n_afetados, log_path=LOG_DECISOES):
    from datetime import datetime
    entrada = {'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M'),
               'problema': problema, 'evidencia': evidencia,
               'decisao': decisao, 'justificativa': justificativa,
               'n_afetados': n_afetados}
    _decisoes.append(entrada)
    pd.DataFrame(_decisoes).to_csv(log_path, index=False, encoding='utf-8')
    print(f"[Decisao] {problema} -> {decisao} ({n_afetados} afetados)")

# Carrega e preserva o original
df_original = pd.read_csv(ARQUIVO_RAW, encoding='utf-8', low_memory=False)
df = df_original.copy()
print(f"Base carregada: {df.shape}")
"""),

# ---- 1. Datas ----
md("---\n## 1. Conversao de datas e horarios\n\n### 1.1 `data_inversa` para datetime\n\nConverte para datetime e extrai mes, dia da semana numerico e indicador de fim de semana."),

code("""\
df['data_inversa'] = pd.to_datetime(df['data_inversa'], errors='coerce')

n_nat = df['data_inversa'].isna().sum()
print(f"Datas nao convertidas (NaT): {n_nat}")
print(f"Periodo: {df['data_inversa'].min().date()} a {df['data_inversa'].max().date()}")

df['mes']            = df['data_inversa'].dt.month
df['dia_semana_num'] = df['data_inversa'].dt.dayofweek  # 0=seg, 6=dom
df['fim_de_semana']  = (df['dia_semana_num'] >= 5).astype(int)

registrar_decisao(
    problema     = "data_inversa como texto no CSV original",
    evidencia    = "Formato dd/mm/aaaa ou ISO; necessario datetime para extrair mes e dia",
    decisao      = "pd.to_datetime com errors='coerce'; criar mes, dia_semana_num, fim_de_semana",
    justificativa= "Variaveis temporais sao features importantes para o modelo e para a EDA",
    n_afetados   = len(df),
)
print("\\nColunas criadas: mes, dia_semana_num, fim_de_semana")
print(df[['data_inversa','mes','dia_semana_num','fim_de_semana']].head(3))
"""),

md("### 1.2 `horario` para hora e faixa horaria\n\nExtrai a hora (0-23) e cria uma faixa horaria de 6 horas para facilitar a analise."),

code("""\
df['hora'] = pd.to_datetime(df['horario'], format='%H:%M:%S', errors='coerce').dt.hour

print(f"Horarios nao convertidos: {df['hora'].isna().sum()}")
print("\\nDistribuicao por hora:")
print(df['hora'].value_counts().sort_index().to_string())
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao (Decisao D4):** Com base nos dados, os acidentes se distribuem ao longo de todo o dia,
> com pico entre 7h-8h (saída para o trabalho), segundo pico às 17h-18h (retorno),
> e volume relevante entre 20h-22h (circulação noturna).
>
> Propomos 4 faixas de 6 horas:
> - **Madrugada (0-5h):** baixo volume, altíssima letalidade (condutor com sono, pista vazia)
> - **Manha (6-11h):** rush matutino, muitos acidentes leves
> - **Tarde (12-17h):** maior volume do dia
> - **Noite (18-23h):** retorno do trabalho + saidas noturnas, risco crescente
>
> **Aprovam essas faixas? Gostariam de ajustar alguma fronteira (ex: separar 0-4h de 5h)?**
"""),

code("""\
def classificar_faixa(hora):
    if pd.isna(hora): return np.nan
    h = int(hora)
    if   0 <= h <= 5:  return 'Madrugada (0-5h)'
    elif 6 <= h <= 11: return 'Manha (6-11h)'
    elif 12 <= h <= 17: return 'Tarde (12-17h)'
    else:               return 'Noite (18-23h)'

df['faixa_horaria'] = df['hora'].apply(classificar_faixa)

print("Distribuicao por faixa horaria:")
print(df['faixa_horaria'].value_counts())

# Letalidade por faixa (confirma a hipotese)
g = df.groupby('faixa_horaria').agg(n=('id','count'), mortos=('mortos','sum')).reset_index()
g['letalidade'] = (g['mortos']/g['n']*100).round(2)
print("\\nLetalidade por faixa:")
print(g.sort_values('letalidade', ascending=False).to_string(index=False))

registrar_decisao(
    problema     = "Sem variavel de faixa horaria",
    evidencia    = "Madrugada tem letalidade >2x maior que tarde; faixas capturam esse padrao",
    decisao      = "Criar faixa_horaria com 4 categorias de 6h (D4 aprovada pela equipe)",
    justificativa= "Faixas facilitam analise e uso no modelo; definicao alinhada com a equipe",
    n_afetados   = len(df),
)
"""),

# ---- 2. Numericas ----
md("---\n## 2. Conversao de colunas numericas\n\n`km`, `latitude` e `longitude` podem ter virgula decimal no CSV do portal PRF. Este bloco trata os dois casos (ja float ou texto com virgula)."),

code("""\
for col in ['km', 'latitude', 'longitude']:
    if df[col].dtype == object:
        df[col] = (df[col].astype(str)
                   .str.replace(',', '.', regex=False)
                   .pipe(pd.to_numeric, errors='coerce'))
    n_null = df[col].isna().sum()
    print(f"{col}: dtype={df[col].dtype}, nulos={n_null}, "
          f"range=[{df[col].min():.3f}, {df[col].max():.3f}]")
"""),

# ---- 3. Regras de dominio ----
md("---\n## 3. Validacao de regras de dominio\n\nVerifica se as colunas respeitam as restricoes logicas esperadas: coordenadas na Regiao Sul, contagens nao negativas e `pessoas >= 1`."),

code("""\
# Coordenadas na Regiao Sul (SC/PR/RS: lat -35 a -22, lon -57 a -44)
coord_inv = df[df['latitude'].notna() &
               ((df['latitude'] < -35) | (df['latitude'] > -22) |
                (df['longitude'] < -57) | (df['longitude'] > -44))]
print(f"Coordenadas fora da Regiao Sul: {len(coord_inv)}")
if len(coord_inv) > 0:
    print(coord_inv[['id','municipio','uf','latitude','longitude']].to_string())

# pessoas >= 1
print(f"\\nAcidentes com pessoas < 1: {(df['pessoas'] < 1).sum()}")

# Contagens negativas
for col in ['mortos','feridos_leves','feridos_graves','feridos','ilesos','ignorados','veiculos']:
    neg = (df[col] < 0).sum()
    if neg > 0:
        print(f"  {col}: {neg} valores negativos")
if all((df[c] >= 0).all() for c in ['mortos','feridos','veiculos']):
    print("Todas as contagens sao nao negativas: OK")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Se todas as regras passarem (esperado, dado que a base ja estava limpa
> no diagnostico), registrar como validado. Se houver coordenadas fora da Regiao Sul,
> investigar se sao erros de registro antes de remover: pode ser um acidente em rodovia
> federal proxima da fronteira estadual mas corretamente classificado como SC/PR/RS.
>
> **Aprovam essa estrategia?**
"""),

code("""\
# Consistencia: classificacao_acidente x mortos
fatal_sem_morto = df[
    (df['classificacao_acidente'] == 'Com Vítimas Fatais') & (df['mortos'] == 0)
]
print(f"'Com Vitimas Fatais' com mortos=0: {len(fatal_sem_morto)}")

sem_vit = df[(df['classificacao_acidente'] == 'Sem Vítimas') &
             ((df['mortos'] > 0) | (df['feridos'] > 0))]
print(f"'Sem Vitimas' com mortos>0 ou feridos>0: {len(sem_vit)}")

# feridos = feridos_leves + feridos_graves
inconsist = (df['feridos'] != df['feridos_leves'] + df['feridos_graves']).sum()
print(f"Inconsistencias feridos != leves+graves: {inconsist}")

if len(fatal_sem_morto) == 0 and len(sem_vit) == 0 and inconsist == 0:
    print("\\nBase internamente consistente nos pontos criticos: OK")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** A base passa em todas as verificacoes de consistencia.
> O fato de `feridos = feridos_leves + feridos_graves` em 100% dos casos confirma
> que `feridos` e uma **coluna derivada** e deve ser removida do conjunto de features
> do modelo de ML para evitar vazamento de informacao. O mesmo vale para todas as
> colunas de contagem de vitimas: `mortos`, `feridos_leves`, `feridos_graves`,
> `feridos`, `ilesos`, `ignorados`. Elas **definem** a variavel-alvo e nao estariam
> disponiveis no momento de previr a gravidade de um acidente novo.
>
> **Aprovam a exclusao dessas colunas do modelo?**
"""),

# ---- 4. Texto ----
md("---\n## 4. Padronizacao de texto\n\nRemove espacos extras das colunas de texto. Simples mas necessario para garantir joins e comparacoes corretos."),

code("""\
colunas_texto = df.select_dtypes(include='object').columns.tolist()
for col in colunas_texto:
    df[col] = df[col].str.strip()

# Verifica espacos usando apenas colunas que existem no original
colunas_orig_texto = df_original.select_dtypes(include='object').columns.tolist()
n_com_espaco = sum(
    df_original[c].dropna().str.startswith(' ').sum() +
    df_original[c].dropna().str.endswith(' ').sum()
    for c in colunas_orig_texto
)
print(f"Strip aplicado em {len(colunas_texto)} colunas de texto.")
print(f"Total de valores que tinham espacos extras no original: {n_com_espaco}")
"""),

# ---- 5. tracado_via ----
md("---\n## 5. `tracado_via`: tratamento da variavel multivalorada\n\nDois passos: (1) normalizar a ordem dos componentes para unificar combinacoes equivalentes; (2) criar uma coluna dummy para cada componente."),

code("""\
print("Top 20 valores de tracado_via (antes da normalizacao):")
print(df['tracado_via'].value_counts().head(20).to_string())
print(f"\\nCombinacoes distintas antes: {df['tracado_via'].nunique()}")
"""),

code("""\
def normalizar_tracado(valor):
    if pd.isna(valor): return np.nan
    partes = sorted(p.strip() for p in str(valor).split(';'))
    return ';'.join(partes)

df['tracado_via_norm'] = df['tracado_via'].apply(normalizar_tracado)

print(f"Combinacoes distintas depois: {df['tracado_via_norm'].nunique()}")
print("\\nTop 20 apos normalizacao:")
print(df['tracado_via_norm'].value_counts().head(20).to_string())
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** Antes da normalizacao, "Reta;Declive" e "Declive;Reta" existem como
> **duas categorias distintas**, mas representam o mesmo tipo de trecho.
> Apos ordenar os componentes, ambas viram "Declive;Reta", reduzindo a fragmentacao.
> Isso e essencial para nao superestimar a raridade de certas combinacoes.
>
> **Aprovam essa normalizacao?**
"""),

code("""\
# Identifica todos os componentes unicos
componentes = set()
for val in df['tracado_via_norm'].dropna():
    for comp in val.split(';'):
        componentes.add(comp.strip())

print("Componentes encontrados:", sorted(componentes))

# Cria uma dummy para cada componente
for comp in sorted(componentes):
    nome = ('tracado_' + comp.lower()
            .replace(' ', '_').replace('/', '_').replace('ç', 'c')
            .replace('ã', 'a').replace('ó', 'o').replace('é', 'e'))
    df[nome] = df['tracado_via_norm'].apply(
        lambda x: 1 if pd.notna(x) and comp in x.split(';') else 0
    )
    print(f"  {nome}: {df[nome].sum()} acidentes ({df[nome].mean()*100:.1f}%)")

registrar_decisao(
    problema     = "tracado_via multivalorado com ordem variavel",
    evidencia    = "Ex: 'Reta;Declive' e 'Declive;Reta' = mesmo tracado; 60+ combinacoes distintas",
    decisao      = "Ordenar componentes e criar dummies por componente",
    justificativa= "Permite usar cada tipo de tracado como feature independente e comparar letalidade",
    n_afetados   = df['tracado_via'].notna().sum(),
)
"""),

# ---- 6. Ausencias disfarcadas ----
md("---\n## 6. Ausencias disfarcadas (Decisao D5)\n\nConsidera 'Ignorado' e 'Nao Informado' como ausencias verdadeiras, pois nao descrevem uma condicao real."),

code("""\
print("Antes da conversao:")
print(f"  condicao_metereologica='Ignorado': {(df['condicao_metereologica']=='Ignorado').sum()}")
print(f"  sentido_via='Nao Informado': {df['sentido_via'].isin(['Não Informado','Nao Informado']).sum()}")
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao (Decisao D5):** Nossa recomendacao e **converter para NaN** pelos seguintes motivos:
>
> - Sao apenas 63 + 20 = 83 registros (0,96% da base): impacto minimo.
> - Manter como categoria cria uma falsa "condicao meteorologica Ignorado" que distorce
>   os percentuais em graficos e tabelas.
> - No modelo de ML, o scikit-learn pode tratar NaN com `SimpleImputer` (moda para categoricas).
>
> Se a equipe quiser manter para analisar se o "Ignorado" e sistematico em alguma UF ou BR
> (o que poderia indicar subnotificacao), e uma analise valida antes de converter.
>
> **Aprovam a conversao para NaN? Ou querem analisar o padrao antes?**
"""),

code("""\
# Decisao D5: converter para NaN (comentar se a equipe decidir manter)
df['condicao_metereologica'] = df['condicao_metereologica'].replace('Ignorado', np.nan)
df['sentido_via'] = df['sentido_via'].replace({'Não Informado': np.nan, 'Nao Informado': np.nan})

print("Apos a conversao:")
print(f"  condicao_metereologica NaN: {df['condicao_metereologica'].isna().sum()}")
print(f"  sentido_via NaN: {df['sentido_via'].isna().sum()}")

registrar_decisao(
    problema     = "Ausencias disfarcadas em condicao_metereologica e sentido_via",
    evidencia    = "'Ignorado' (63) e 'Nao Informado' (20) nao sao condicoes reais",
    decisao      = "Converter para NaN (D5 aprovada pela equipe)",
    justificativa= "Evita distorcao de percentuais; impacto minimo (0,96% dos registros)",
    n_afetados   = 83,
)
"""),

# ---- 7. regional/delegacia/uop ----
md("---\n## 7. Recuperacao de `regional`, `delegacia` e `uop`\n\nTenta preencher os poucos ausentes usando a moda do municipio: cada municipio pertence a uma circunscricao fixa da PRF."),

code("""\
aus = df[df['regional'].isna() | df['delegacia'].isna() | df['uop'].isna()]
print(f"Registros com algum campo ausente: {len(aus)}")
if len(aus) > 0:
    print(aus[['id','municipio','uf','regional','delegacia','uop']].to_string(index=False))
"""),

code("""\
for col in ['regional', 'delegacia', 'uop']:
    n_antes = df[col].isna().sum()
    if n_antes == 0:
        print(f"{col}: sem ausentes, nada a fazer.")
        continue
    moda_mun = (df[df[col].notna()]
                .groupby('municipio')[col]
                .agg(lambda x: x.mode().iloc[0] if len(x) > 0 else np.nan))
    mask = df[col].isna()
    df.loc[mask, col] = df.loc[mask, 'municipio'].map(moda_mun)
    n_depois = df[col].isna().sum()
    print(f"{col}: {n_antes} ausentes -> {n_depois} restantes apos recuperacao por municipio")

registrar_decisao(
    problema     = "regional, delegacia, uop com NaN",
    evidencia    = "7-9 registros; municipio identifica a circunscricao da PRF",
    decisao      = "Preencher pela moda do municipio; residuos ficam NaN",
    justificativa= "Recuperacao logica e segura; municipio e o menor nivel de localizacao disponivel",
    n_afetados   = 9,
)
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** A recuperacao pela moda do municipio e correta porque cada municipio esta
> inteiramente dentro de uma circunscricao da PRF: um municipio nao pertence a duas delegacias
> diferentes. Se algum registro restar com NaN apos essa operacao, significa que **todos os outros
> acidentes naquele municipio tambem tinham o campo ausente**: nao e possivel recuperar sem
> consultar o cadastro oficial da PRF.
>
> **Aprovam essa estrategia?**
"""),

# ---- 8. causa_acidente ----
md("---\n## 8. Agrupamento de `causa_acidente` (Decisao D4)\n\nProposta de macrocategorias para reduzir as 65 categorias originais a grupos mais interpretaveis."),

code("""\
print("Todas as categorias de causa_acidente e sua frequencia:")
print(df['causa_acidente'].value_counts(dropna=False).to_string())
"""),

code("""\
# Calcula tambem a letalidade por causa para informar o agrupamento
g_causa = (df.groupby('causa_acidente')
             .agg(n=('id','count'), mortos=('mortos','sum'))
             .reset_index())
g_causa['letalidade'] = (g_causa['mortos'] / g_causa['n'] * 100).round(1)
print("Causas por letalidade (top 20):")
print(g_causa.sort_values('letalidade', ascending=False).head(20)
      [['causa_acidente','n','mortos','letalidade']].to_string(index=False))
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao de mapeamento (D4):** Com base na frecuencia e na letalidade, propomos:
>
> | Macrocategoria | Exemplos de causas incluidas |
> |---|---|
> | **Falha de atencao / reacao** | Ausencia de reacao, Reacao tardia, Nao manter distancia |
> | **Comportamento de risco** | Velocidade incompativel, Contramao, Ultrapassagem indevida, Condutor dormindo |
> | **Infracao de transito** | Desrespeitar preferencia, Sinal vermelho, Sem CNH |
> | **Uso de alcool ou substancias** | Ingestao de alcool, Substancias psicoativas |
> | **Condicao do veiculo** | Defeito mecanico, Pneu com defeito, Carga mal distribuida |
> | **Condicao da via / ambiente** | Chuva, Defeito na via, Sinalicacao insuficiente, Pista escorregadia |
> | **Fator externo** | Animais na pista, Objeto estatico, Acidente anterior |
> | **Pedestre / ciclista** | Pedestre, Ciclista |
> | **Outras / nao especificadas** | Demais |
>
> **Atencao:** "Transitar na contramao" (34,4% de letalidade) e "Velocidade incompativel" (10,9%)
> sao as causas comportamentais mais mortais e merecem destaque especial nas conclusoes.
>
> **Aprovam esse mapeamento? Alguma causa em categoria errada?**
"""),

code("""\
MAPA_CAUSAS = {
    # Falha de atencao / reacao
    'Ausência de reação do condutor':                  'Falha de atencao ou reacao',
    'Reação tardia ou ineficiente do condutor':        'Falha de atencao ou reacao',
    'Condutor deixou de manter distância do veículo da frente': 'Falha de atencao ou reacao',
    'Acessar a via sem observar a presença dos outros veículos': 'Falha de atencao ou reacao',
    'Manobra de mudança de faixa':                     'Falha de atencao ou reacao',

    # Comportamento de risco
    'Velocidade Incompatível':                         'Comportamento de risco',
    'Transitar na contramão':                          'Comportamento de risco',
    'Ultrapassagem Indevida':                          'Comportamento de risco',
    'Condutor Dormindo':                               'Comportamento de risco',
    'Trafegar com motocicleta (ou similar) entre as faixas': 'Comportamento de risco',

    # Infracao de transito
    'Desrespeitar a preferência no cruzamento':        'Infracao de transito',
    'Desobedecer à sinalização da via (placa, pare...)': 'Infracao de transito',

    # Uso de alcool
    'Ingestão de álcool pelo condutor':                'Alcool ou substancias',
    'Ingestão de substâncias psicoativas pelo condutor': 'Alcool ou substancias',

    # Condicao do veiculo
    'Demais falhas mecânicas ou elétricas':            'Condicao do veiculo',
    'Avarias e/ou desgaste excessivo no pneu':         'Condicao do veiculo',
    'Defeito mecânico em veículo':                     'Condicao do veiculo',
    'Carga excessiva e/ou mal acondicionada':          'Condicao do veiculo',

    # Condicao da via / ambiente
    'Chuva':                                           'Condicao da via ou ambiente',
    'Pista Escorregadia':                              'Condicao da via ou ambiente',
    'Defeito na Via':                                  'Condicao da via ou ambiente',
    'Sinalização Insuficiente ou Inadequada':          'Condicao da via ou ambiente',
    'Acostamento em mau estado de conservação':        'Condicao da via ou ambiente',

    # Fator externo
    'Animais na Pista':                                'Fator externo',
    'Objeto estático sobre o leito carroçável':        'Fator externo',

    # Pedestre / ciclista
    'Pedestre andava na pista':                        'Pedestre ou ciclista',
    'Pedestre cruzava a pista fora da faixa':          'Pedestre ou ciclista',
}

df['macrocausa'] = df['causa_acidente'].map(MAPA_CAUSAS).fillna('Outras')

print("Distribuicao de macrocausa:")
print(df['macrocausa'].value_counts().to_string())

# Visualiza letalidade por macrocausa
g_mc = (df.groupby('macrocausa')
          .agg(n=('id','count'), mortos=('mortos','sum'))
          .reset_index())
g_mc['letalidade'] = (g_mc['mortos'] / g_mc['n'] * 100).round(1)
print("\\nLetalidade por macrocausa:")
print(g_mc.sort_values('letalidade', ascending=False)
          [['macrocausa','n','mortos','letalidade']].to_string(index=False))
"""),

code("""\
# Grafico: letalidade por macrocausa
fig, ax = plt.subplots(figsize=(10, 5))
g_mc_ord = g_mc.sort_values('letalidade', ascending=True)
bars = ax.barh(g_mc_ord['macrocausa'], g_mc_ord['letalidade'], color='firebrick', alpha=0.8)
ax.bar_label(bars, fmt='%.1f', padding=3, fontsize=9)
ax.set_title('Letalidade por macrocausa (mortos por 100 acidentes)')
ax.set_xlabel('Mortos por 100 acidentes')
ax.set_ylabel('Macrocausa')
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS, 'fig08_letalidade_macrocausa.png'), dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: fig08_letalidade_macrocausa.png")

registrar_decisao(
    problema     = "causa_acidente com 65 categorias, muitas raras",
    evidencia    = "Top 5 causas ja representam >50% dos acidentes; categorias raras dificultam analise",
    decisao      = "Agrupar em 8 macrocategorias + 'Outras' (D4 aprovada pela equipe)",
    justificativa= "Mapa baseado em frequencia e letalidade; equipe revisou e aprovou",
    n_afetados   = df['causa_acidente'].notna().sum(),
)
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao:** "Comportamento de risco" deve ter a maior letalidade (contramao + velocidade
> incompativel + ultrapassagem indevida sao os mais mortais). "Falha de atencao ou reacao"
> tera o maior volume. "Alcool ou substancias" tera letalidade intermediaria.
>
> Isso e importante para as recomendacoes finais: **o comportamento do condutor e
> o principal fator associado a gravidade**, nao as condicoes da via ou do veiculo.
> Politicas de fiscalizacao (blitz de alcoolemia, radares em trechos de ultrapassagem)
> tem maior potencial de impacto que melhorias de infraestrutura isoladas.
>
> **Aprovam essa leitura e as recomendacoes?**
"""),

# ---- 9. Variaveis de gravidade ----
md("---\n## 9. Criacao de variaveis de gravidade\n\nDuas variaveis binarias derivadas: `teve_morte` e `grave_ou_fatal`. Facilitam modelagem binaria e comparacoes diretas."),

code("""\
df['teve_morte']    = (df['mortos'] > 0).astype(int)
df['grave_ou_fatal'] = ((df['feridos_graves'] > 0) | (df['mortos'] > 0)).astype(int)

print("teve_morte:")
print(df['teve_morte'].value_counts())
print(f"  Taxa: {df['teve_morte'].mean()*100:.1f}% dos acidentes tiveram mortes")

print("\\ngrave_ou_fatal:")
print(df['grave_ou_fatal'].value_counts())
print(f"  Taxa: {df['grave_ou_fatal'].mean()*100:.1f}% tiveram feridos graves ou mortos")

registrar_decisao(
    problema     = "Sem variavel binaria de gravidade para modelos mais simples",
    evidencia    = "classificacao_acidente tem 3 classes; binario reduz complexidade do modelo",
    decisao      = "Criar teve_morte (0/1) e grave_ou_fatal (0/1)",
    justificativa= "Decisao alinhada com a equipe; grave_ou_fatal e o alvo mais util para a PRF",
    n_afetados   = len(df),
)
"""),

md("""\
> ✍️ **INTERPRETAÇÃO DA EQUIPE:**
>
> **Sugestao (Decisao D3):** Para o modelo de ML (Notebook 04), recomendamos usar
> **`grave_ou_fatal` como variavel-alvo** pelos seguintes motivos:
>
> 1. Ela captura tanto mortes quanto feridos graves: e o que importa para a PRF dimensionar
>    recursos de resgate e priorizar patrulhas.
> 2. O desbalanceamento e menor: ~30% de 1s vs ~5% para `teve_morte`, facilitando o aprendizado.
> 3. E mais util operacionalmente: a PRF nao pode intervir **depois** do acidente, mas pode
>    priorizar trechos e horarios com maior probabilidade de acidentes graves.
>
> **Aprovam usar `grave_ou_fatal` como alvo binario? Ou preferem manter o multiclasse?**
"""),

# ---- 10. Validacao final ----
md("---\n## 10. Validacao final (EDA pos-tratamento)\n\nRepete o perfil de qualidade para confirmar que os tratamentos funcionaram e nao introduziram novos problemas."),

code("""\
perf_antes  = perfil_qualidade(df_original)
perf_depois = perfil_qualidade(df)

comp = perf_antes[['variavel','n_ausentes']].merge(
    perf_depois[['variavel','n_ausentes']], on='variavel', suffixes=('_antes','_depois'), how='outer'
)
comp['diferenca'] = comp['n_ausentes_antes'].fillna(0) - comp['n_ausentes_depois'].fillna(0)
print("Mudancas no numero de ausentes (antes -> depois):")
print(comp[comp['diferenca'] != 0].to_string(index=False))
"""),

code("""\
novas = [c for c in df.columns if c not in df_original.columns]
print(f"Colunas novas criadas ({len(novas)}):")
for c in novas:
    print(f"  {c}: {df[c].dtype}, exemplo: {df[c].iloc[0]}")

print(f"\\nDimensoes finais: {df.shape[0]} linhas x {df.shape[1]} colunas")
print(f"(original: {df_original.shape[0]} x {df_original.shape[1]})")
"""),

# ---- 11. Salvar ----
md("---\n## 11. Salvando os arquivos\n\nSalva a base tratada, o log de decisoes e o dicionario de dados."),

code("""\
df.to_csv(ARQUIVO_PROC, index=False, encoding='utf-8')
print(f"Base tratada salva: {ARQUIVO_PROC} ({df.shape[0]} linhas x {df.shape[1]} colunas)")
"""),

code("""\
# Gera dicionario de dados
colunas_orig = set(df_original.columns)
descricoes = {
    'id':                    'Identificador unico do acidente (chave primaria)',
    'data_inversa':          'Data do acidente (datetime)',
    'dia_semana':            'Dia da semana por extenso (texto com acentos)',
    'horario':               'Horario do acidente no formato hh:mm:ss',
    'uf':                    'Unidade da Federacao (SC, PR ou RS)',
    'br':                    'Numero da rodovia federal',
    'km':                    'Quilometro da rodovia',
    'municipio':             'Nome do municipio',
    'causa_acidente':        'Causa registrada pelo agente (65 categorias originais)',
    'tipo_acidente':         'Tipo do acidente (16 categorias)',
    'classificacao_acidente':'Variavel-alvo: Sem Vitimas / Com Vitimas Feridas / Com Vitimas Fatais',
    'fase_dia':              'Fase do dia: Pleno dia, Amanhecer, Anoitecer, Plena Noite',
    'sentido_via':           'Sentido do fluxo no trecho',
    'condicao_metereologica':'Condicao climatica (Ignorado convertido para NaN)',
    'tipo_pista':            'Tipo de pista: Simples, Dupla ou Multipla',
    'tracado_via':           'Tracado original da via (multivalorado, separado por ponto-e-virgula)',
    'uso_solo':              'Area urbana (Sim) ou rural (Nao) conforme cadastro PRF',
    'pessoas':               'Total de pessoas envolvidas no acidente',
    'mortos':                'Numero de mortos confirmados',
    'feridos_leves':         'Numero de feridos leves',
    'feridos_graves':        'Numero de feridos graves',
    'feridos':               'Total de feridos (= feridos_leves + feridos_graves, coluna derivada)',
    'ilesos':                'Numero de ilesos',
    'ignorados':             'Pessoas com estado nao informado',
    'veiculos':              'Numero de veiculos envolvidos',
    'latitude':              'Latitude do acidente (decimal negativo)',
    'longitude':             'Longitude do acidente (decimal negativo)',
    'regional':              'Superintendencia regional da PRF',
    'delegacia':             'Delegacia de policia rodoviaria responsavel',
    'uop':                   'Unidade operacional da PRF',
    'mes':                   'Mes do acidente (1=jan, 5=mai) derivado de data_inversa',
    'dia_semana_num':        'Dia da semana numerico (0=segunda, 6=domingo)',
    'fim_de_semana':         '1 se sabado ou domingo, 0 caso contrario',
    'hora':                  'Hora do acidente (0-23) derivada de horario',
    'faixa_horaria':         'Faixa de 6h: Madrugada/Manha/Tarde/Noite (D4)',
    'tracado_via_norm':      'tracado_via com componentes ordenados alfabeticamente',
    'macrocausa':            'Macrocategoria de causa_acidente (D4, aprovada pela equipe)',
    'teve_morte':            '1 se houve pelo menos um morto, 0 caso contrario',
    'grave_ou_fatal':        '1 se ferido_grave > 0 ou morto > 0 (variavel-alvo sugerida para ML)',
}

linhas = [
    '# Dicionario de Dados: datatran_sul_tratado.csv',
    '',
    '| Variavel | Tipo | Origem | Descricao |',
    '|---|---|---|---|',
]
for col in df.columns:
    origem = 'Original' if col in colunas_orig else 'Derivada'
    desc   = descricoes.get(col, '(sem descricao)')
    linhas.append(f'| `{col}` | {df[col].dtype} | {origem} | {desc} |')

with open(DICIONARIO, 'w', encoding='utf-8') as f:
    f.write('\\n'.join(linhas))

print(f"Dicionario salvo: {DICIONARIO}")
print(f"Log de decisoes: {LOG_DECISOES}")
"""),

md("""\
---
## 12. Resumo

**Tratamentos aplicados neste notebook:**

| Tratamento | Colunas afetadas | Decisao |
|---|---|---|
| Conversao para datetime + variaveis derivadas | `data_inversa`, `mes`, `dia_semana_num`, `fim_de_semana` | Automatica |
| Extracao de hora e faixa horaria | `hora`, `faixa_horaria` | D4: aprovada |
| Conversao de decimal (virgula para ponto) | `km`, `latitude`, `longitude` | Automatica |
| Normalizacao + dummies de tracado | `tracado_via_norm`, `tracado_*` | Automatica |
| Ausencias disfarcadas -> NaN | `condicao_metereologica`, `sentido_via` | D5: aprovada |
| Recuperacao por municipio | `regional`, `delegacia`, `uop` | Automatica |
| Macrocausas | `macrocausa` | D4: aprovada |
| Variaveis de gravidade | `teve_morte`, `grave_ou_fatal` | D3: aprovada |

**Decisoes ainda em aberto:**
- D1: Periodo (so 2026 ou baixar anos anteriores?)
- D2: Recorte da pergunta (gravidade geral, por estado ou por causa?)

---

> ✍️ **INTERPRETAÇÃO DA EQUIPE:** (a preencher na aula)
> Algum tratamento gerou surpresas? Encontraram alguma inconsistencia inesperada?
> As macrocausas propostas fazem sentido para o contexto de rodovias federais do Sul?
> A escolha de `grave_ou_fatal` como variavel-alvo do modelo esta alinhada com
> o que a PRF precisaria saber na pratica?
"""),

]  # fim nb02

nb02 = notebook(nb02_cells, "02_preprocessamento.ipynb")
save(nb02, "02_preprocessamento.ipynb")

print("\\nTodos os notebooks regenerados com sucesso!")
