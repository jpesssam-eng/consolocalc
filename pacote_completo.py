"""
ConsoloCalc - Modulo de empacotamento ZIP
==========================================
Empacota todos os artefatos do dimensionamento (PDF, Excel, CSV, PNGs,
README) em um unico arquivo ZIP, pronto para download e anexacao a
projetos ou trabalhos academicos.

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

import io
import zipfile
from dataclasses import replace
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from consolo_calc import DadosConsolo, dimensionar
from exportar import gerar_csv, gerar_excel
from memorial_pdf import gerar_pdf
from visualizacao import desenhar_consolo


# ============================================================
# Cores (consistentes com os demais modulos)
# ============================================================
COR_TIRANTE = "#CC0000"
COR_COSTURA = "#FF6600"
COR_PRIMARIA = "#1A4F7A"


def _gerar_grafico_sensibilidade_png(dados: DadosConsolo, parametro: str,
                                     inicio: float, fim: float, passo: float,
                                     metodo: str = "iterativo",
                                     titulo_param: str = "parametro",
                                     unidade: str = "") -> bytes:
    """
    Gera grafico de sensibilidade em PNG (matplotlib) variando um parametro
    e mostrando como as armaduras se comportam.

    Retorna os bytes da imagem PNG.
    """
    valores = np.arange(inicio, fim + passo / 2, passo)
    as_tirante, as_costura, x_valid = [], [], []

    for v in valores:
        try:
            dados_var = replace(dados, **{parametro: float(v)})
            r = dimensionar(dados_var, metodo=metodo)
            if r["tipo"] == "longo":
                continue
            as_tirante.append(r["As_tirante"])
            as_costura.append(r["As_costura"])
            x_valid.append(float(v))
        except Exception:
            continue

    fig, ax = plt.subplots(figsize=(9, 5.5))
    if x_valid:
        ax.plot(x_valid, as_tirante, color=COR_TIRANTE, linewidth=2.5,
                marker="o", markersize=7, label="A$_s$ tirante")
        ax.plot(x_valid, as_costura, color=COR_COSTURA, linewidth=2.5,
                marker="s", markersize=7, linestyle="--",
                label="A$_s$ costura")

        # Marca o valor atual do parametro
        valor_atual = getattr(dados, parametro)
        ax.axvline(x=valor_atual, color="gray", linestyle=":",
                   alpha=0.7, label=f"Valor atual: {valor_atual:g}")

    label_x = f"{titulo_param} ({unidade})" if unidade else titulo_param
    ax.set_xlabel(label_x, fontsize=12, fontweight="bold")
    ax.set_ylabel("Area de aco (cm²)", fontsize=12, fontweight="bold")
    ax.set_title(f"Analise de sensibilidade - variacao de {titulo_param}",
                 fontsize=13, fontweight="bold", color=COR_PRIMARIA)
    ax.legend(loc="best", fontsize=11)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _gerar_diagrama_png(dados: DadosConsolo, resultado: dict) -> bytes:
    """Gera o diagrama do consolo em PNG."""
    fig = desenhar_consolo(dados, resultado)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _gerar_readme(dados: DadosConsolo, resultado: dict, metodo: str) -> str:
    """Gera README textual descrevendo o pacote."""
    ts = datetime.now().strftime("%d/%m/%Y as %H:%M")
    biela = resultado["biela"]
    status_biela = "OK" if biela["ok"] else "ESMAGADA — RISCO DE RUPTURA"

    metodo_descricao = {
        "iterativo": "iterativo (z = d - 0,4*x, atualizado por convergencia)",
        "simplificado": "simplificado (z = 0,85*d, estimativa fixa)",
    }.get(metodo, metodo)

    iteracoes_txt = ""
    if metodo == "iterativo":
        iteracoes_txt = f"  Iteracoes ate convergencia: {resultado.get('iteracoes', 'n/a')}\n"

    return f"""===========================================================
  ConsoloCalc - Pacote de Resultados
  Dimensionamento de consolos curtos de concreto armado
  Conforme NBR 6118:2023
===========================================================

  Gerado em {ts}.

-----------------------------------------------------------
  ARQUIVOS INCLUIDOS NESTE PACOTE
-----------------------------------------------------------

  01_memorial_calculo.pdf
      Memorial de calculo completo, formatado em A4,
      pronto para anexar a projetos executivos.

  02_planilha_dados.xlsx
      Planilha Excel com 3 abas (dados de entrada,
      resultados detalhados e memorial textual).

  03_dados.csv
      Arquivo CSV com todos os parametros e resultados
      em formato chave-valor, pronto para importacao em
      Power BI, Google Sheets ou outras ferramentas de
      analise de dados.

  04_diagrama_consolo.png
      Diagrama esquematico do consolo com geometria,
      modelo de bielas e tirantes e cotas. Resolucao
      150 dpi, pronto para insercao em documentos.

  05_sensibilidade_Vk.png
      Grafico de analise de sensibilidade variando a
      forca vertical Vk de 50% a 200% do valor atual.

  README.txt
      Este arquivo, com sumario do caso analisado e
      dos arquivos incluidos.

-----------------------------------------------------------
  DADOS DE ENTRADA
-----------------------------------------------------------

  Materiais:
    fck (concreto) ........ {dados.fck:.1f} MPa
    fyk (aco) ............. {dados.fyk:.1f} MPa

  Geometria (cm):
    a (carga - face pilar). {dados.a:.1f}
    h (altura) ............ {dados.h:.1f}
    b (largura) ........... {dados.b:.1f}
    d' (cobrimento) ....... {dados.d_linha:.1f}

  Esforcos (kN):
    Vk (vertical) ......... {dados.Vk:.1f}
    Hk (horizontal) ....... {dados.Hk:.1f}
    Impedimento horizontal: {'Sim' if dados.impedimento_horizontal else 'Nao'}

  Metodo de calculo de z:
    {metodo_descricao}
{iteracoes_txt}
-----------------------------------------------------------
  RESULTADOS PRINCIPAIS
-----------------------------------------------------------

  Classificacao: consolo {resultado['tipo']}
  Relacao a/d = {resultado['razao_ad']:.3f}
  Altura util d = {resultado['d']:.2f} cm

  Esforcos de calculo:
    Vd = {resultado['Vd']:.2f} kN
    Hd = {resultado['Hd']:.2f} kN

  Modelo de bielas e tirantes:
    Braco de alavanca z = {resultado['z']:.2f} cm
    Angulo da biela theta = {resultado['theta_deg']:.2f} graus
    Forca no tirante Rsd = {resultado['Rsd']:.2f} kN
    Forca na biela Fc = {resultado['Fc']:.2f} kN

  Armaduras dimensionadas:
    As tirante = {resultado['As_tirante']:.3f} cm²
    As costura = {resultado['As_costura']:.3f} cm²

  Verificacao da biela comprimida:
    sigma atuante = {biela['sigma_atuante_MPa']:.2f} MPa
    sigma limite  = {biela['sigma_limite_MPa']:.2f} MPa
    aproveitamento = {biela['razao']*100:.1f}%
    Status: {status_biela}

-----------------------------------------------------------
  SOBRE A FERRAMENTA
-----------------------------------------------------------

  ConsoloCalc e uma aplicacao web de codigo aberto para
  dimensionamento de consolos curtos de concreto armado
  segundo a NBR 6118:2023, pelo metodo de bielas e
  tirantes.

  Aplicacao publica..... https://consolocalc.streamlit.app
  Codigo-fonte.......... https://github.com/jpesssam-eng/consolocalc
  Licenca............... MIT

  Desenvolvida como Trabalho de Conclusao de Curso
  do Centro Universitario Internacional UNINTER.

===========================================================
"""


def gerar_pacote_zip(dados: DadosConsolo, resultado: dict,
                     metodo: str = "iterativo") -> bytes:
    """
    Empacota todos os artefatos do dimensionamento em um unico
    arquivo ZIP. Retorna os bytes prontos para download.

    Conteudo do ZIP:
        01_memorial_calculo.pdf
        02_planilha_dados.xlsx
        03_dados.csv
        04_diagrama_consolo.png
        05_sensibilidade_Vk.png
        README.txt
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w",
                         compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. PDF
        zf.writestr("01_memorial_calculo.pdf", gerar_pdf(dados, resultado))

        # 2. Excel
        zf.writestr("02_planilha_dados.xlsx", gerar_excel(dados, resultado))

        # 3. CSV
        zf.writestr("03_dados.csv", gerar_csv(dados, resultado))

        # 4. Diagrama PNG
        zf.writestr("04_diagrama_consolo.png",
                    _gerar_diagrama_png(dados, resultado))

        # 5. Grafico de sensibilidade (variando Vk como padrao)
        v_atual = dados.Vk if dados.Vk > 0 else 100.0
        png_sens = _gerar_grafico_sensibilidade_png(
            dados,
            parametro="Vk",
            inicio=max(10.0, v_atual * 0.5),
            fim=v_atual * 2.0,
            passo=max(5.0, v_atual * 0.1),
            metodo=metodo,
            titulo_param="Vk (forca vertical)",
            unidade="kN",
        )
        zf.writestr("05_sensibilidade_Vk.png", png_sens)

        # 6. README
        zf.writestr("README.txt", _gerar_readme(dados, resultado, metodo))

    return zip_buffer.getvalue()
