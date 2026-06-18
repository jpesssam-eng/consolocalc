"""
ConsoloCalc - Modulo de visualizacao
=====================================
Funcoes para gerar diagramas esquematicos do consolo
mostrando geometria, carga aplicada e modelo de bielas e tirantes.

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

import matplotlib
matplotlib.use("Agg")  # backend sem interface (necessario no servidor)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np


def desenhar_consolo(dados, resultado):
    """
    Gera um diagrama esquematico do consolo curto mostrando:
    - Geometria (pilar + consolo) com hachura
    - Carga aplicada (Vk) com seta vermelha
    - Modelo de bielas e tirantes (biela tracejada azul + tirante vermelho)
    - Angulo theta da biela
    - Cotas principais (a, h, d, d')
    """
    fig, ax = plt.subplots(figsize=(10, 7), dpi=100)
    fig.patch.set_facecolor("white")

    # ===== Dimensoes =====
    a = float(dados.a)
    h = float(dados.h)
    d_linha = float(dados.d_linha)
    d = h - d_linha
    pilar_w = max(20.0, h / 3.0)
    base_extra = 10.0
    consolo_face = a + 8.0

    # ===== Pilar =====
    pilar = Rectangle(
        (-pilar_w, -base_extra), pilar_w, h + 2 * base_extra,
        facecolor="#D3D3D3", edgecolor="black", linewidth=2,
        hatch="///", alpha=0.7
    )
    ax.add_patch(pilar)

    # ===== Consolo =====
    consolo = Rectangle(
        (0, 0), consolo_face, h,
        facecolor="#E8E8E8", edgecolor="black", linewidth=2,
        hatch="///", alpha=0.7
    )
    ax.add_patch(consolo)

    # ===== Tirante (linha vermelha no topo) =====
    y_tirante = h - d_linha
    ax.plot(
        [0, consolo_face], [y_tirante, y_tirante],
        color="#CC0000", linewidth=3, label="Tirante (tracao)", zorder=5
    )
    # Posicoes das barras
    for x in np.linspace(2, consolo_face - 2, 5):
        ax.plot(x, y_tirante, "o", color="#CC0000", markersize=6, zorder=6)

    # ===== Biela (linha tracejada azul inclinada) =====
    ax.plot(
        [0, a], [0, y_tirante],
        color="#0066CC", linewidth=3, linestyle="--",
        label="Biela (compressao)", zorder=5
    )

    # ===== Seta da carga Vk =====
    ax.annotate(
        "", xy=(a, h), xytext=(a, h + 15),
        arrowprops=dict(arrowstyle="->", lw=2.5, color="red"),
        zorder=10
    )
    ax.text(
        a + 1.5, h + 8, f"$V_k$ = {dados.Vk:.0f} kN",
        fontsize=12, color="red", fontweight="bold"
    )

    # ===== Angulo theta =====
    theta_deg = resultado["theta_deg"]
    raio_arc = min(14, a * 0.6)
    arc = patches.Arc(
        (0, 0), raio_arc * 2, raio_arc * 2, angle=0,
        theta1=0, theta2=theta_deg, color="#0066CC", linewidth=2
    )
    ax.add_patch(arc)
    ax.text(
        raio_arc * 0.55, raio_arc * 0.25,
        f"θ = {theta_deg:.1f}°",
        fontsize=11, color="#0066CC", fontweight="bold"
    )

    # ===== Cota 'a' =====
    cota_y = -base_extra + 2
    ax.annotate(
        "", xy=(a, cota_y), xytext=(0, cota_y),
        arrowprops=dict(arrowstyle="<->", lw=1.5, color="black")
    )
    ax.text(
        a / 2, cota_y - 3.5, f"a = {a:.0f} cm",
        ha="center", fontsize=11, fontweight="bold"
    )
    ax.plot([0, 0], [cota_y - 1, cota_y + 1], "k-", linewidth=1)
    ax.plot([a, a], [cota_y - 1, cota_y + 1], "k-", linewidth=1)

    # ===== Cota 'h' =====
    cota_x = consolo_face + 3
    ax.annotate(
        "", xy=(cota_x, h), xytext=(cota_x, 0),
        arrowprops=dict(arrowstyle="<->", lw=1.5, color="black")
    )
    ax.text(
        cota_x + 1.5, h / 2, f"h = {h:.0f} cm",
        va="center", fontsize=11, fontweight="bold", rotation=90
    )

    # ===== Cota 'd' (altura util) =====
    ax.annotate(
        "", xy=(consolo_face + 1, y_tirante), xytext=(consolo_face + 1, 0),
        arrowprops=dict(arrowstyle="<->", lw=1, color="gray")
    )
    ax.text(
        consolo_face - 1.5, y_tirante / 2, f"d = {d:.1f} cm",
        va="center", fontsize=9, color="gray", rotation=90
    )

    # ===== Configuracoes finais =====
    ax.set_xlim(-pilar_w - 5, consolo_face + 15)
    ax.set_ylim(-base_extra - 7, h + 22)
    ax.set_aspect("equal")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.set_xlabel("Posicao horizontal (cm)", fontsize=10)
    ax.set_ylabel("Posicao vertical (cm)", fontsize=10)

    titulo = f"Consolo {resultado['tipo']} — a/d = {resultado['razao_ad']:.3f}"
    ax.set_title(titulo, fontsize=13, fontweight="bold", pad=15)

    ax.legend(loc="upper left", fontsize=10, framealpha=0.95)

    plt.tight_layout()
    return fig
