"""Gerador do Notebook 04: Modelo de Classificacao de Gravidade (ABEX VI)."""
import json, textwrap

def md(source): return {"cell_type": "markdown", "metadata": {}, "source": [source]}
def code(source): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [source]}

cells = []

# ── Cabecalho ────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    # Notebook 04: Modelo de Classificacao de Gravidade
    **ABEX VI: Projeto Integrado III**
    Equipe: Gabriel Victor Rosario, Joao Wictor Decarli, Rafael Lucas Rockenbach, Bernardo Dal Piva Bernardi

    ---

    **Objetivo:** Treinar modelos de classificacao binaria para prever se um acidente resultara em
    vitima grave ou fatal (`grave_ou_fatal = 1`), usando apenas variaveis de contexto conhecidas
    antes do desfecho.

    **Entradas:**
    - `data/processed/datatran_sul_tratado.csv`

    **Saidas:**
    - `reports/figuras/fig20_baseline_vs_modelos.png`
    - `reports/figuras/fig21_confusion_matrix_lr.png`
    - `reports/figuras/fig22_confusion_matrix_dt.png`
    - `reports/figuras/fig23_confusion_matrix_rf.png`
    - `reports/figuras/fig24_importancia_features.png`

    **Perguntas respondidas:**
    1. Quais variaveis de contexto melhor predizem a gravidade de um acidente?
    2. Qual modelo tem melhor desempenho (F1 macro) para prever acidentes graves/fatais?
    3. O modelo e util para apoiar decisoes preventivas da PRF/DNIT?

    **Limitacao declarada:** A base cobre apenas jan-mai/2026. Sem dados de volume de trafego
    (exposicao), os padroes aprendidos refletem caracteristicas dos registros, nao risco absoluto.\
""")))

# ── Imports ──────────────────────────────────────────────────────────────────
cells.append(md("## 0. Configuracao do ambiente\n\nImporta bibliotecas e define caminhos."))

cells.append(code(textwrap.dedent("""\
    import os, sys, warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    import seaborn as sns
    warnings.filterwarnings('ignore')

    _raiz = ('.' if os.path.exists(os.path.join('.', 'data', 'processed', 'datatran_sul_tratado.csv')) else '..')
    sys.path.insert(0, os.path.join(_raiz, 'src'))
    try:
        from utils import perfil_qualidade
    except ImportError:
        def perfil_qualidade(df):
            return pd.DataFrame({
                'tipo': df.dtypes,
                'ausentes': df.isnull().sum(),
                'pct_ausentes': (df.isnull().mean() * 100).round(2),
                'unicos': df.nunique()
            })

    from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.impute import SimpleImputer
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        classification_report, confusion_matrix, ConfusionMatrixDisplay,
        f1_score, precision_score, recall_score
    )

    plt.rcParams.update({'figure.dpi': 150, 'font.size': 11})
    print("Bibliotecas carregadas com sucesso.")\
""")))

# ── Colab / path ──────────────────────────────────────────────────────────────
cells.append(code(textwrap.dedent("""\
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        BASE_DIR = '/content/drive/MyDrive/abex-vi'
    except ImportError:
        if os.path.exists(os.path.join('data', 'processed', 'datatran_sul_tratado.csv')):
            BASE_DIR = '.'
        else:
            BASE_DIR = '..'

    ARQUIVO_PROC  = os.path.join(BASE_DIR, 'data', 'processed', 'datatran_sul_tratado.csv')
    DIR_FIGURAS   = os.path.join(BASE_DIR, 'reports', 'figuras')
    os.makedirs(DIR_FIGURAS, exist_ok=True)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"Arquivo processado: {os.path.abspath(ARQUIVO_PROC)}")\
""")))

# ── Carga ────────────────────────────────────────────────────────────────────
cells.append(md("## 1. Carregamento da base tratada\n\nCarrega a base produzida pelo Notebook 02 e faz uma verificacao rapida."))

cells.append(code(textwrap.dedent("""\
    df = pd.read_csv(ARQUIVO_PROC)
    print(f"Linhas x colunas: {df.shape}")
    print(f"\\nDistribuicao do alvo:")
    vc = df['grave_ou_fatal'].value_counts()
    pct = df['grave_ou_fatal'].value_counts(normalize=True) * 100
    resumo = pd.DataFrame({'n': vc, '%': pct.round(1)})
    resumo.index = ['Sem gravidade (0)', 'Grave ou fatal (1)']
    print(resumo)\
""")))

# ── Vazamento ────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 2. Vazamento de dados: o que NAO pode ser feature

    Esta secao e critica para a validade do modelo. As colunas abaixo descrevem o
    **desfecho** do acidente: elas so sao conhecidas DEPOIS que o acidente aconteceu.
    Usar qualquer uma delas como feature seria vazamento de dados (data leakage):
    o modelo aprenderia a "prever" algo que ja aconteceu, inflando artificialmente
    as metricas sem nenhuma utilidade pratica.

    | Coluna excluida | Motivo |
    |---|---|
    | `mortos` | Define `teve_morte` e contribui para `grave_ou_fatal` |
    | `feridos_graves` | Contribui diretamente para `grave_ou_fatal` |
    | `feridos_leves` | Desfecho, nao contexto |
    | `feridos` | Soma de feridos_leves + feridos_graves |
    | `ilesos` | Desfecho |
    | `ignorados` | Desfecho |
    | `teve_morte` | Derivada de `mortos`, desfecho |
    | `classificacao_acidente` | Define o alvo |

    Features permitidas: apenas variaveis de **contexto** conhecidas antes ou no momento
    do registro (local, condicoes, tipo de via, horario, causa, numero de veiculos/pessoas).\
""")))

# ── Features ─────────────────────────────────────────────────────────────────
cells.append(md("## 3. Selecao de features\n\nDefine as colunas de entrada do modelo separando numericas e categoricas."))

cells.append(code(textwrap.dedent("""\
    ALVO = 'grave_ou_fatal'

    # Colunas de desfecho a excluir (vazamento)
    EXCLUIR = [
        'mortos', 'feridos_leves', 'feridos_graves', 'feridos',
        'ilesos', 'ignorados', 'teve_morte', 'classificacao_acidente',
        # Identificadores e datas brutas
        'id', 'data_inversa', 'horario',
        # Geograficas detalhadas (municipio/km podem ser proxies de rota, mas municipio
        # tem cardinalidade muito alta; km e mantido como numerico)
        'municipio', 'regional', 'delegacia', 'uop',
        # tracado_via_norm e a versao textual; os dummies ja estao incluidos
        'tracado_via', 'tracado_via_norm',
        # O proprio alvo
        ALVO,
    ]

    FEATURES_NUM = [
        'br', 'km', 'pessoas', 'veiculos',
        'mes', 'dia_semana_num', 'fim_de_semana', 'hora',
        'tracado_aclive', 'tracado_curva', 'tracado_declive',
        'tracado_reta', 'tracado_intersecao_de_vias',
        'tracado_ponte', 'tracado_rotatoria', 'tracado_viaduto',
    ]

    FEATURES_CAT = [
        'uf', 'dia_semana', 'fase_dia', 'condicao_metereologica',
        'tipo_pista', 'uso_solo', 'faixa_horaria',
        'macrocausa', 'tipo_acidente', 'sentido_via',
    ]

    FEATURES = FEATURES_NUM + FEATURES_CAT

    X = df[FEATURES].copy()
    y = df[ALVO].copy()

    print(f"Features numericas ({len(FEATURES_NUM)}): {FEATURES_NUM}")
    print(f"\\nFeatures categoricas ({len(FEATURES_CAT)}): {FEATURES_CAT}")
    print(f"\\nTotal de features: {len(FEATURES)}")
    print(f"Alvo: {ALVO} | Positivos (grave/fatal): {y.sum()} ({y.mean()*100:.1f}%)")\
""")))

# ── Desbalanceamento ──────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 4. Desbalanceamento de classes

    Com 75,4% da classe 0 e 24,6% da classe 1, o modelo pode aprender a chutar sempre 0
    e ainda ter 75% de acuracia. Por isso usaremos `class_weight='balanced'` nos modelos
    e avaliaremos pelo **F1 macro** (media das F1 por classe), nao pela acuracia.\
""")))

cells.append(code(textwrap.dedent("""\
    fig, ax = plt.subplots(figsize=(6, 4))
    cores = ['#4878CF', '#D65F5F']
    rotulos = ['Sem gravidade\\n(0)', 'Grave ou fatal\\n(1)']
    contagens = y.value_counts().sort_index()
    bars = ax.bar(rotulos, contagens.values, color=cores, edgecolor='white', width=0.5)
    for bar, n in zip(bars, contagens.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{n}\\n({n/len(y)*100:.1f}%)', ha='center', va='bottom', fontsize=10)
    ax.set_title('Distribuicao do alvo: grave_ou_fatal')
    ax.set_ylabel('Numero de acidentes')
    ax.set_ylim(0, contagens.max() * 1.15)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig20_distribuicao_alvo.png'))
    plt.show()
    print("Figura salva: fig20_distribuicao_alvo.png")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: destaque que 75% dos acidentes nao sao graves/fatais. Se o modelo apenas chutasse
    > sempre 0, acertaria 75% dos casos, mas erraria 100% dos graves. Isso justifica usar
    > class_weight='balanced' e F1 macro como metrica principal.\
""")))

# ── Pipeline ──────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 5. Preprocessamento para ML

    Constroi um `ColumnTransformer` com:
    - Numericas: imputacao pela mediana + padronizacao (StandardScaler)
    - Categoricas: imputacao pela moda + codificacao one-hot (ignora categorias novas no teste)\
""")))

cells.append(code(textwrap.dedent("""\
    pipe_num = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler',  StandardScaler()),
    ])

    pipe_cat = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot',  OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])

    preprocessador = ColumnTransformer([
        ('num', pipe_num, FEATURES_NUM),
        ('cat', pipe_cat, FEATURES_CAT),
    ])
    print("Preprocessador criado com sucesso.")\
""")))

# ── Split ────────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 6. Divisao treino/teste

    Divide os dados estratificando pelo alvo para manter a proporcao de classes em ambos
    os conjuntos. Usa 80% para treino e 20% para teste. `random_state=42` garante
    reprodutibilidade.\
""")))

cells.append(code(textwrap.dedent("""\
    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"Treino: {X_treino.shape[0]} amostras | Teste: {X_teste.shape[0]} amostras")
    print(f"Proporcao grave/fatal no treino: {y_treino.mean()*100:.1f}%")
    print(f"Proporcao grave/fatal no teste:  {y_teste.mean()*100:.1f}%")\
""")))

# ── Baseline ─────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 7. Baseline ingênuo (DummyClassifier)

    Ponto de partida: um classificador que sempre prediz a classe majoritaria (0).
    Todo modelo real deve superar esse baseline para ser util.\
""")))

cells.append(code(textwrap.dedent("""\
    baseline = Pipeline([
        ('pre', preprocessador),
        ('clf', DummyClassifier(strategy='most_frequent', random_state=42)),
    ])
    baseline.fit(X_treino, y_treino)
    y_pred_bl = baseline.predict(X_teste)

    print("=== BASELINE (classe majoritaria) ===")
    print(classification_report(y_teste, y_pred_bl,
                                 target_names=['Sem gravidade (0)', 'Grave/fatal (1)']))
    print(f"F1 macro: {f1_score(y_teste, y_pred_bl, average='macro'):.3f}")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: o baseline tem recall 0 para a classe 1, ou seja, nao detecta nenhum acidente
    > grave. Qualquer modelo util precisa ter F1 macro acima deste valor.\
""")))

# ── Regressao Logistica ───────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 8. Regressao Logistica

    Modelo linear, interpretavel e rapido. `class_weight='balanced'` compensa o
    desbalanceamento aumentando o peso dos exemplos da classe minoritaria no treinamento.\
""")))

cells.append(code(textwrap.dedent("""\
    lr = Pipeline([
        ('pre', preprocessador),
        ('clf', LogisticRegression(
            class_weight='balanced', max_iter=1000, random_state=42, solver='lbfgs'
        )),
    ])
    lr.fit(X_treino, y_treino)
    y_pred_lr = lr.predict(X_teste)

    print("=== REGRESSAO LOGISTICA ===")
    print(classification_report(y_teste, y_pred_lr,
                                 target_names=['Sem gravidade (0)', 'Grave/fatal (1)']))
    print(f"F1 macro: {f1_score(y_teste, y_pred_lr, average='macro'):.3f}")\
""")))

cells.append(code(textwrap.dedent("""\
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_teste, y_pred_lr)
    disp = ConfusionMatrixDisplay(cm, display_labels=['Sem gravidade', 'Grave/fatal'])
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_title('Matriz de Confusao: Regressao Logistica')
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig21_confusion_matrix_lr.png'))
    plt.show()
    print("Figura salva: fig21_confusion_matrix_lr.png")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: observe o recall da classe 1 (grave/fatal). Para a PRF, e mais importante
    > detectar acidentes graves (recall alto) do que evitar alarmes falsos (precisao).\
""")))

# ── Arvore de Decisao ─────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 9. Arvore de Decisao

    Modelo nao-linear, altamente interpretavel: e possivel visualizar as regras de decisao.
    `max_depth=6` limita o overfitting. `class_weight='balanced'` para o desbalanceamento.\
""")))

cells.append(code(textwrap.dedent("""\
    dt = Pipeline([
        ('pre', preprocessador),
        ('clf', DecisionTreeClassifier(
            max_depth=6, class_weight='balanced', random_state=42
        )),
    ])
    dt.fit(X_treino, y_treino)
    y_pred_dt = dt.predict(X_teste)

    print("=== ARVORE DE DECISAO (max_depth=6) ===")
    print(classification_report(y_teste, y_pred_dt,
                                 target_names=['Sem gravidade (0)', 'Grave/fatal (1)']))
    print(f"F1 macro: {f1_score(y_teste, y_pred_dt, average='macro'):.3f}")\
""")))

cells.append(code(textwrap.dedent("""\
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_teste, y_pred_dt)
    disp = ConfusionMatrixDisplay(cm, display_labels=['Sem gravidade', 'Grave/fatal'])
    disp.plot(ax=ax, colorbar=False, cmap='Greens')
    ax.set_title('Matriz de Confusao: Arvore de Decisao')
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig22_confusion_matrix_dt.png'))
    plt.show()
    print("Figura salva: fig22_confusion_matrix_dt.png")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: compare com a regressao logistica. A arvore tende a ter melhor recall para
    > a classe minoritaria. Observe se houve melhora no F1 macro.\
""")))

# ── Random Forest ─────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 10. Random Forest

    Ensemble de arvores: geralmente mais robusto que uma arvore unica.
    Usamos `n_estimators=200` e `class_weight='balanced'`. Serve tambem para
    calcular importancia das features.\
""")))

cells.append(code(textwrap.dedent("""\
    rf = Pipeline([
        ('pre', preprocessador),
        ('clf', RandomForestClassifier(
            n_estimators=200, max_depth=10, class_weight='balanced',
            random_state=42, n_jobs=-1
        )),
    ])
    rf.fit(X_treino, y_treino)
    y_pred_rf = rf.predict(X_teste)

    print("=== RANDOM FOREST (200 arvores, max_depth=10) ===")
    print(classification_report(y_teste, y_pred_rf,
                                 target_names=['Sem gravidade (0)', 'Grave/fatal (1)']))
    print(f"F1 macro: {f1_score(y_teste, y_pred_rf, average='macro'):.3f}")\
""")))

cells.append(code(textwrap.dedent("""\
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_teste, y_pred_rf)
    disp = ConfusionMatrixDisplay(cm, display_labels=['Sem gravidade', 'Grave/fatal'])
    disp.plot(ax=ax, colorbar=False, cmap='Oranges')
    ax.set_title('Matriz de Confusao: Random Forest')
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig23_confusion_matrix_rf.png'))
    plt.show()
    print("Figura salva: fig23_confusion_matrix_rf.png")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: o Random Forest costuma ter o melhor desempenho geral, mas e menos interpretavel
    > que a arvore simples. Considere se o ganho em F1 justifica a perda de explicabilidade
    > para a PRF e o DNIT.\
""")))

# ── Comparacao ────────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 11. Comparacao dos modelos

    Resume as metricas dos tres modelos e do baseline num unico grafico.\
""")))

cells.append(code(textwrap.dedent("""\
    def metricas(y_true, y_pred, nome):
        return {
            'Modelo': nome,
            'F1 macro': f1_score(y_true, y_pred, average='macro'),
            'F1 classe 1': f1_score(y_true, y_pred, pos_label=1),
            'Recall classe 1': recall_score(y_true, y_pred, pos_label=1),
            'Precisao classe 1': precision_score(y_true, y_pred, pos_label=1),
        }

    resultados = pd.DataFrame([
        metricas(y_teste, y_pred_bl, 'Baseline'),
        metricas(y_teste, y_pred_lr, 'Reg. Logistica'),
        metricas(y_teste, y_pred_dt, 'Arvore (depth=6)'),
        metricas(y_teste, y_pred_rf, 'Random Forest'),
    ]).set_index('Modelo')

    print(resultados.round(3).to_string())

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(resultados))
    w = 0.2
    metr_cols = ['F1 macro', 'F1 classe 1', 'Recall classe 1', 'Precisao classe 1']
    cores_bar = ['#4878CF', '#D65F5F', '#6ACC65', '#B47CC7']
    for i, (col, cor) in enumerate(zip(metr_cols, cores_bar)):
        ax.bar(x + i*w, resultados[col], w, label=col, color=cor, edgecolor='white')
    ax.set_xticks(x + w*1.5)
    ax.set_xticklabels(resultados.index, rotation=15, ha='right')
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Valor da metrica')
    ax.set_title('Comparacao de modelos: metricas por classe grave/fatal')
    ax.legend(loc='upper right', fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig20_baseline_vs_modelos.png'))
    plt.show()
    print("Figura salva: fig20_baseline_vs_modelos.png")\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: identifique qual modelo tem maior F1 macro e qual tem maior recall para a
    > classe 1. Explique o trade-off entre recall (detectar o maximo de acidentes graves)
    > e precisao (evitar alertas falsos). Para uma aplicacao de seguranca viaria, recall
    > tende a ser mais importante.\
""")))

# ── Importancia ───────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 12. Importancia das features (Random Forest)

    Mostra quais variaveis mais contribuiram para as predicoes do Random Forest.
    Importante: importancia indica associacao estatistica, nao relacao de causa e efeito.\
""")))

cells.append(code(textwrap.dedent("""\
    # Recupera nomes das features apos o one-hot encoding
    cat_encoder = rf.named_steps['pre'].named_transformers_['cat'].named_steps['onehot']
    cat_nomes = cat_encoder.get_feature_names_out(FEATURES_CAT).tolist()
    todos_nomes = FEATURES_NUM + cat_nomes

    importancias = rf.named_steps['clf'].feature_importances_
    imp_df = pd.Series(importancias, index=todos_nomes).sort_values(ascending=False)

    # Agrupa por feature original (soma das dummies one-hot)
    imp_orig = {}
    for feat in FEATURES_NUM:
        idx = todos_nomes.index(feat)
        imp_orig[feat] = importancias[idx]
    for feat in FEATURES_CAT:
        cols = [n for n in todos_nomes if n.startswith(feat + '_')]
        imp_orig[feat] = sum(importancias[todos_nomes.index(c)] for c in cols)

    imp_orig = pd.Series(imp_orig).sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, 7))
    cores_imp = ['#D65F5F' if imp_orig[f] >= imp_orig.quantile(0.75) else '#4878CF'
                 for f in imp_orig.index]
    ax.barh(imp_orig.index, imp_orig.values, color=cores_imp, edgecolor='white')
    ax.set_xlabel('Importancia (Gini impurity reducao media)')
    ax.set_title('Importancia das features: Random Forest\\n(vermelho = top 25%)')
    ax.spines[['top', 'right']].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_FIGURAS, 'fig24_importancia_features.png'))
    plt.show()
    print("Figura salva: fig24_importancia_features.png")
    print("\\nTop 5 features mais importantes:")
    print(imp_orig.sort_values(ascending=False).head(5))\
""")))

cells.append(md(textwrap.dedent("""\
    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: observe quais variaveis aparecem no topo. Esperamos que `tipo_acidente`,
    > `macrocausa`, `pessoas` e `veiculos` tenham alta importancia. Destaque que
    > importancia alta nao significa causalidade: a variavel pode ser indicador de
    > risco sem ser a causa direta. Discuta implicacoes para a PRF/DNIT.\
""")))

# ── Leitura Critica ───────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 13. Leitura critica e limitacoes

    - **Associacao, nao causa:** as features importantes indicam correlacao com
      gravidade, nao que causam o acidente grave.
    - **Sem volume de trafego:** nao temos dados de fluxo de veiculos. Uma BR movimentada
      pode ter mais acidentes graves simplesmente por ter mais veiculos.
    - **5 meses de dados:** a base cobre jan-mai/2026. Eventos sazonais (feriados, chuvas
      de verao) podem distorcer os padroes aprendidos.
    - **Alvo derivado:** `grave_ou_fatal` foi construido a partir das contagens de vitimas.
      A qualidade do modelo depende da qualidade do registro pela PRF.
    - **Uso etico:** o modelo pode apoiar alocacao preventiva de recursos (patrulhamento,
      sinalizacao), mas nao deve ser usado para discriminar rodovias sem analise humana.\
""")))

# ── Resumo Final ─────────────────────────────────────────────────────────────
cells.append(md(textwrap.dedent("""\
    ---
    ## 14. Resumo

    **Produzido neste notebook:**

    | Artefato | Descricao |
    |---|---|
    | `fig20_distribuicao_alvo.png` | Distribuicao da variavel alvo (balanceamento) |
    | `fig20_baseline_vs_modelos.png` | Comparacao de F1 macro e metricas por classe |
    | `fig21_confusion_matrix_lr.png` | Matriz de confusao: Regressao Logistica |
    | `fig22_confusion_matrix_dt.png` | Matriz de confusao: Arvore de Decisao |
    | `fig23_confusion_matrix_rf.png` | Matriz de confusao: Random Forest |
    | `fig24_importancia_features.png` | Importancia das features no Random Forest |

    **Decisoes registradas:** D3 (alvo binario `grave_ou_fatal`), D1 (somente 2026).

    > ✍️ **INTERPRETACAO DA EQUIPE:** (a preencher)
    > Dica: resuma em 3 a 5 frases os resultados do melhor modelo, quais variaveis mais
    > importam, e o que isso significa para a PRF e o DNIT. Lembre de citar as limitacoes
    > da base (5 meses, sem volume de trafego).\
""")))

# ── Montar e salvar ───────────────────────────────────────────────────────────
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"}
    },
    "cells": cells
}

import os as _os
caminho = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)), 'notebooks', '04_modelo_gravidade.ipynb'
)
_os.makedirs(_os.path.dirname(caminho), exist_ok=True)
with open(caminho, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook gerado: {caminho}")
print(f"Total de celulas: {len(cells)}")
