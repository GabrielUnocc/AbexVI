"""
utils.py - Funções reutilizáveis do projeto ABEX VI
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency


# ---------------------------------------------------------------------------
# Perfil de qualidade
# ---------------------------------------------------------------------------

def perfil_qualidade(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna um DataFrame com tipo, ausentes, % ausentes e únicos de cada coluna."""
    resultado = []
    for col in df.columns:
        n_aus = df[col].isna().sum()
        resultado.append({
            "variavel": col,
            "tipo": str(df[col].dtype),
            "n_ausentes": n_aus,
            "pct_ausentes": round(n_aus / len(df) * 100, 2),
            "n_unicos": df[col].nunique(dropna=False),
        })
    return pd.DataFrame(resultado)


# ---------------------------------------------------------------------------
# Log de decisões de pré-processamento
# ---------------------------------------------------------------------------

LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports", "decisoes_preprocessamento.csv"
)

_decisoes: list[dict] = []


def registrar_decisao(
    problema: str,
    evidencia: str,
    decisao: str,
    justificativa: str,
    n_afetados: int,
    log_path: str = LOG_PATH,
) -> None:
    """Registra uma decisão de pré-processamento no CSV de log."""
    from datetime import datetime

    entrada = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "problema": problema,
        "evidencia": evidencia,
        "decisao": decisao,
        "justificativa": justificativa,
        "n_afetados": n_afetados,
    }
    _decisoes.append(entrada)

    df_log = pd.DataFrame(_decisoes)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    df_log.to_csv(log_path, index=False, encoding="utf-8")
    print(f"[Decisao registrada] {problema} -> {decisao} ({n_afetados} afetados)")


# ---------------------------------------------------------------------------
# V de Cramér
# ---------------------------------------------------------------------------

def cramers_v(x: pd.Series, y: pd.Series) -> float:
    """Calcula o V de Cramér entre duas variáveis categóricas."""
    tabela = pd.crosstab(x, y)
    chi2, _, _, _ = chi2_contingency(tabela)
    n = tabela.values.sum()
    min_dim = min(tabela.shape) - 1
    if min_dim == 0 or n == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * min_dim)))


# ---------------------------------------------------------------------------
# Índice de letalidade
# ---------------------------------------------------------------------------

def indice_letalidade(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Mortos por 100 acidentes, agrupado por uma variável categórica."""
    agg = (
        df.groupby(grupo)
        .agg(n_acidentes=("id", "count"), total_mortos=("mortos", "sum"))
        .reset_index()
    )
    agg["letalidade_por_100"] = (agg["total_mortos"] / agg["n_acidentes"] * 100).round(2)
    return agg.sort_values("letalidade_por_100", ascending=False)


# ---------------------------------------------------------------------------
# Análise de outliers por IQR
# ---------------------------------------------------------------------------

def outliers_iqr(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Retorna linhas com valores fora de 1,5 * IQR na coluna indicada."""
    q1 = df[coluna].quantile(0.25)
    q3 = df[coluna].quantile(0.75)
    iqr = q3 - q1
    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr
    mask = (df[coluna] < limite_inf) | (df[coluna] > limite_sup)
    print(f"{coluna}: Q1={q1}, Q3={q3}, IQR={iqr:.2f}, "
          f"limites=[{limite_inf:.2f}, {limite_sup:.2f}], "
          f"outliers={mask.sum()}")
    return df[mask]
