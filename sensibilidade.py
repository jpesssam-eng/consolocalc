"""
ConsoloCalc - Modulo de analise de sensibilidade
==================================================
Funcoes para gerar graficos interativos de analise paramétrica,
mostrando como os resultados do dimensionamento variam em funcao
de cada parametro de entrada.

Os graficos sao gerados com Plotly (interativos no navegador).

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

from dataclasses import replace

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from consolo_calc import DadosConsolo, dimensionar


# ============================================================
# Cores padrao
# ============================================================
COR_PRIMARIA = "#1A4F7A"
COR_BIELA = "#0066CC"
COR_TIRANTE = "#CC0000"
COR_COSTURA = "#FF6600"
COR_OK = "#2E7D32"
COR_ALERTA = "#F57F17"
COR_ERRO = "#C62828"


def _intervalo_padrao(parametro: str, valor_atual: float):
    """
    Retorna (min, max, passo) padrao para cada parametro,
    centralizado no valor atual.
    """
    if parametro == "a":
        return max(5.0, valor_atual * 0.3), valor_atual * 2.0, 1.0
    if parametro == "h":
        return max(15.0, valor_atual * 0.5), valor_atual * 1.8, 2.0
    if parametro == "b":
        return max(10.0, valor_atual * 0.5), valor_atual * 2.0, 2.0
    if parametro == "fck":
        return 20.0, 60.0, 5.0
    if parametro == "Vk":
        return max(10.0, valor_atual * 0.2), valor_atual * 2.5, 10.0
    if parametro == "Hk":
        return 0.0, max(50.0, valor_atual * 2.0 if valor_atual else 50.0), 5.0
    if parametro == "d_linha":
        return 2.0, 8.0, 0.5
    return valor_atual * 0.5, valor_atual * 1.5, 1.0


def gerar_serie(dados_base: DadosConsolo, parametro: str,
                inicio: float, fim: float, passo: float):
    """
    Gera uma serie de resultados variando um parametro e mantendo
    os demais constantes.

    Retorna uma lista de dicionarios com:
        valor_parametro, tipo, As_tirante, As_costura, Rsd, Fc,
        aproveitamento_biela, biela_ok
    """
    valores = np.arange(inicio, fim + passo / 2, passo)
    resultados = []

    for v in valores:
        # Cria uma copia do DadosConsolo substituindo o parametro
        dados_var = replace(dados_base, **{parametro: float(v)})
        try:
            r = dimensionar(dados_var)
            # Pula consolos longos (fora do escopo do modelo)
            if r["tipo"] == "longo":
                continue
            resultados.append({
                "parametro_valor": float(v),
                "tipo": r["tipo"],
                "razao_ad": r["razao_ad"],
                "As_tirante": r["As_tirante"],
                "As_costura": r["As_costura"],
                "Rsd": r["Rsd"],
                "Fc": r["Fc"],
                "aproveitamento_biela": r["biela"]["razao"] * 100,
                "biela_ok": r["biela"]["ok"],
            })
        except Exception:
            continue

    return resultados


def grafico_armaduras(serie, parametro_nome: str, unidade: str):
    """
    Gera grafico de barras/linhas mostrando As_tirante e As_costura
    em funcao do parametro variado.
    """
    x = [r["parametro_valor"] for r in serie]
    y_tir = [r["As_tirante"] for r in serie]
    y_cost = [r["As_costura"] for r in serie]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y_tir, mode="lines+markers",
        name="A<sub>s</sub> tirante",
        line=dict(color=COR_TIRANTE, width=3),
        marker=dict(size=8, symbol="circle"),
        hovertemplate=(
            f"{parametro_nome} = %{{x:.2f}} {unidade}<br>"
            "A<sub>s</sub> tirante = %{y:.2f} cm²<extra></extra>"
        ),
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y_cost, mode="lines+markers",
        name="A<sub>s</sub> costura",
        line=dict(color=COR_COSTURA, width=3, dash="dot"),
        marker=dict(size=8, symbol="square"),
        hovertemplate=(
            f"{parametro_nome} = %{{x:.2f}} {unidade}<br>"
            "A<sub>s</sub> costura = %{y:.2f} cm²<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=f"Armaduras em funcao de {parametro_nome}",
        xaxis_title=f"{parametro_nome} ({unidade})",
        yaxis_title="Área de aço (cm²)",
        hovermode="x unified",
        template="simple_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    )
    return fig


def grafico_aproveitamento_biela(serie, parametro_nome: str, unidade: str):
    """
    Gera grafico de aproveitamento da biela, com faixas coloridas
    indicando seguranca, alerta e ruptura.
    """
    x = [r["parametro_valor"] for r in serie]
    y = [r["aproveitamento_biela"] for r in serie]

    fig = go.Figure()

    # Faixas coloridas de fundo
    if x:
        x_min, x_max = min(x), max(x)
        # Faixa segura (0-80%)
        fig.add_shape(type="rect", x0=x_min, x1=x_max, y0=0, y1=80,
                      fillcolor=COR_OK, opacity=0.08, line_width=0,
                      layer="below")
        # Faixa alerta (80-100%)
        fig.add_shape(type="rect", x0=x_min, x1=x_max, y0=80, y1=100,
                      fillcolor=COR_ALERTA, opacity=0.15, line_width=0,
                      layer="below")
        # Faixa ruptura (>100%)
        y_top = max(120, max(y) * 1.05) if y else 120
        fig.add_shape(type="rect", x0=x_min, x1=x_max, y0=100, y1=y_top,
                      fillcolor=COR_ERRO, opacity=0.15, line_width=0,
                      layer="below")
        # Linhas limite
        fig.add_hline(y=80, line=dict(color=COR_ALERTA, width=1, dash="dash"),
                      annotation_text="80% (alerta)",
                      annotation_position="right")
        fig.add_hline(y=100, line=dict(color=COR_ERRO, width=1.5, dash="dash"),
                      annotation_text="100% (ruptura)",
                      annotation_position="right")

    # Curva principal
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        name="Aproveitamento",
        line=dict(color=COR_BIELA, width=3),
        marker=dict(size=8),
        hovertemplate=(
            f"{parametro_nome} = %{{x:.2f}} {unidade}<br>"
            "Aproveitamento = %{y:.1f}%<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=f"Aproveitamento da biela em funcao de {parametro_nome}",
        xaxis_title=f"{parametro_nome} ({unidade})",
        yaxis_title="Aproveitamento (%)",
        template="simple_white",
        height=400,
        showlegend=False,
    )
    return fig


def grafico_forcas(serie, parametro_nome: str, unidade: str):
    """
    Gera grafico mostrando as forcas Rsd (tirante) e Fc (biela)
    em funcao do parametro variado.
    """
    x = [r["parametro_valor"] for r in serie]
    y_rsd = [r["Rsd"] for r in serie]
    y_fc = [r["Fc"] for r in serie]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y_rsd, mode="lines+markers",
        name="R<sub>sd</sub> (tirante)",
        line=dict(color=COR_TIRANTE, width=3),
        marker=dict(size=8),
        hovertemplate=(
            f"{parametro_nome} = %{{x:.2f}} {unidade}<br>"
            "R<sub>sd</sub> = %{y:.2f} kN<extra></extra>"
        ),
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y_fc, mode="lines+markers",
        name="F<sub>c</sub> (biela)",
        line=dict(color=COR_BIELA, width=3, dash="dot"),
        marker=dict(size=8, symbol="square"),
        hovertemplate=(
            f"{parametro_nome} = %{{x:.2f}} {unidade}<br>"
            "F<sub>c</sub> = %{y:.2f} kN<extra></extra>"
        ),
    ))
    fig.update_layout(
        title=f"Forcas no modelo em funcao de {parametro_nome}",
        xaxis_title=f"{parametro_nome} ({unidade})",
        yaxis_title="Forca (kN)",
        hovermode="x unified",
        template="simple_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1),
    )
    return fig


def tabela_parametrica(serie):
    """Retorna a serie como lista de dicionarios para uso em st.dataframe."""
    return [{
        "Valor do parametro": round(r["parametro_valor"], 2),
        "Tipo": r["tipo"],
        "a/d": round(r["razao_ad"], 3),
        "Rsd (kN)": round(r["Rsd"], 2),
        "Fc (kN)": round(r["Fc"], 2),
        "As tirante (cm²)": round(r["As_tirante"], 2),
        "As costura (cm²)": round(r["As_costura"], 2),
        "Aproveitamento biela (%)": round(r["aproveitamento_biela"], 1),
        "Status biela": "OK" if r["biela_ok"] else "ESMAGADA",
    } for r in serie]
