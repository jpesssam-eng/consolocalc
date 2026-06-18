"""
ConsoloCalc - Modulo de geracao de memorial em PDF
====================================================
Funcoes para gerar o memorial de calculo em PDF
com formatacao profissional, incluindo dados de entrada,
calculos, resultados e o diagrama esquematico.

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

from io import BytesIO
from datetime import datetime

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)

from visualizacao import desenhar_consolo


# ============================================================
# Paleta de cores (estilo Uninter, sobrio e profissional)
# ============================================================
COR_PRIMARIA = colors.HexColor("#1A4F7A")
COR_OK = colors.HexColor("#2E7D32")
COR_ERRO = colors.HexColor("#C62828")
COR_FUNDO_LINHA = colors.HexColor("#F0F0F0")


def _criar_estilos():
    """Cria e retorna o conjunto de estilos de paragrafo do PDF."""
    base = getSampleStyleSheet()
    estilos = {
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Heading1"], fontSize=16,
            alignment=TA_CENTER, spaceAfter=8, textColor=COR_PRIMARIA,
        ),
        "subtitulo_pagina": ParagraphStyle(
            "SubPag", parent=base["Normal"], fontSize=11,
            alignment=TA_CENTER, textColor=colors.gray,
        ),
        "secao": ParagraphStyle(
            "Secao", parent=base["Heading2"], fontSize=12,
            spaceBefore=14, spaceAfter=6, textColor=COR_PRIMARIA,
        ),
        "corpo": ParagraphStyle(
            "Corpo", parent=base["Normal"], fontSize=10,
            alignment=TA_JUSTIFY, leading=14,
        ),
        "rodape": ParagraphStyle(
            "Rodape", parent=base["Normal"], fontSize=8,
            alignment=TA_CENTER, textColor=colors.gray,
        ),
    }
    return estilos


def _estilo_tabela():
    """Estilo padrao para as tabelas do memorial."""
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_FUNDO_LINHA]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ])


def gerar_pdf(dados, resultado) -> bytes:
    """
    Gera o memorial de calculo em PDF e retorna como bytes.

    O PDF contem: cabecalho, dados de entrada, classificacao,
    esforcos de calculo, modelo de bielas e tirantes, armaduras,
    verificacao da biela e diagrama esquematico.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Memorial de Calculo - ConsoloCalc",
        author="ConsoloCalc",
    )

    e = _criar_estilos()
    blocos = []

    # ===== Cabecalho =====
    blocos.append(Paragraph("MEMORIAL DE CÁLCULO", e["titulo"]))
    blocos.append(Paragraph(
        "Dimensionamento de consolo curto de concreto armado",
        e["subtitulo_pagina"],
    ))
    blocos.append(Paragraph(
        "Método de bielas e tirantes — NBR 6118:2023",
        e["subtitulo_pagina"],
    ))
    blocos.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        e["subtitulo_pagina"],
    ))
    blocos.append(Spacer(1, 0.4 * cm))

    # ===== 1. Dados de entrada =====
    blocos.append(Paragraph("1. DADOS DE ENTRADA", e["secao"]))
    tab_entrada = [
        ["Parâmetro", "Valor", "Unidade"],
        ["f<sub>ck</sub> (resistência do concreto)", f"{dados.fck:.0f}", "MPa"],
        ["f<sub>yk</sub> (resistência do aço)", f"{dados.fyk:.0f}", "MPa"],
        ["a (distância da carga à face do pilar)", f"{dados.a:.1f}", "cm"],
        ["h (altura do consolo)", f"{dados.h:.1f}", "cm"],
        ["b (largura do consolo)", f"{dados.b:.1f}", "cm"],
        ["d' (cobrimento até CG da armadura)", f"{dados.d_linha:.1f}", "cm"],
        ["V<sub>k</sub> (força vertical característica)", f"{dados.Vk:.2f}", "kN"],
        ["H<sub>k</sub> (força horizontal característica)", f"{dados.Hk:.2f}", "kN"],
        ["Impedimento horizontal",
         "Sim" if dados.impedimento_horizontal else "Não", "-"],
    ]
    # Converter primeira coluna em Paragraph (para suportar subscritos)
    linhas = [tab_entrada[0]]
    for linha in tab_entrada[1:]:
        linhas.append([Paragraph(linha[0], e["corpo"]), linha[1], linha[2]])
    t1 = Table(linhas, colWidths=[8.5 * cm, 4 * cm, 3 * cm])
    t1.setStyle(_estilo_tabela())
    blocos.append(t1)

    # ===== 2. Classificacao =====
    blocos.append(Paragraph("2. CLASSIFICAÇÃO DO CONSOLO", e["secao"]))
    classif = (
        f"Altura útil: d = h − d' = {dados.h:.1f} − {dados.d_linha:.1f} = "
        f"<b>{resultado['d']:.1f} cm</b>.<br/>"
        f"Relação a/d = {dados.a:.1f} / {resultado['d']:.1f} = "
        f"<b>{resultado['razao_ad']:.3f}</b>.<br/>"
        f"Classificação conforme NBR 6118:2023: "
        f"<b>consolo {resultado['tipo'].upper()}</b>."
    )
    blocos.append(Paragraph(classif, e["corpo"]))

    # ===== 3. Esforcos de calculo =====
    blocos.append(Paragraph("3. ESFORÇOS DE CÁLCULO", e["secao"]))
    esforcos = (
        f"Coeficiente de majoração das ações: γ<sub>f</sub> = 1,4.<br/>"
        f"V<sub>d</sub> = 1,4 × {dados.Vk:.2f} = "
        f"<b>{resultado['Vd']:.2f} kN</b>.<br/>"
        f"H<sub>d</sub> = <b>{resultado['Hd']:.2f} kN</b>.<br/>"
        f"Excentricidade: e = (H<sub>d</sub>/V<sub>d</sub>) × d' = "
        f"<b>{resultado['e']:.3f} cm</b>."
    )
    blocos.append(Paragraph(esforcos, e["corpo"]))

    # ===== 4. Modelo bielas e tirantes =====
    blocos.append(Paragraph("4. MODELO DE BIELAS E TIRANTES", e["secao"]))
    modelo = (
        f"Braço de alavanca: z = 0,85 · d = "
        f"<b>{resultado['z']:.2f} cm</b>.<br/>"
        f"Ângulo da biela: θ = arctan(z/a) = "
        f"<b>{resultado['theta_deg']:.2f}°</b>.<br/>"
        f"Força de tração no tirante: R<sub>sd</sub> = "
        f"<b>{resultado['Rsd']:.2f} kN</b>.<br/>"
        f"Força de compressão na biela: F<sub>c</sub> = "
        f"<b>{resultado['Fc']:.2f} kN</b>."
    )
    blocos.append(Paragraph(modelo, e["corpo"]))

    # ===== 5. Armaduras =====
    blocos.append(Paragraph("5. ARMADURAS CALCULADAS", e["secao"]))
    tab_arm = [
        ["Elemento", "Área de aço (cm²)"],
        ["Tirante principal (A_s)", f"{resultado['As_tirante']:.2f}"],
        ["Costura (A_s,cost)", f"{resultado['As_costura']:.2f}"],
    ]
    t2 = Table(tab_arm, colWidths=[10 * cm, 5 * cm])
    t2.setStyle(_estilo_tabela())
    blocos.append(t2)

    # ===== 6. Verificacao da biela =====
    blocos.append(Paragraph("6. VERIFICAÇÃO DA BIELA COMPRIMIDA", e["secao"]))
    biela = resultado["biela"]
    verif = (
        f"Tensão atuante: σ<sub>atuante</sub> = "
        f"<b>{biela['sigma_atuante_MPa']:.2f} MPa</b>.<br/>"
        f"Tensão limite: σ<sub>lim</sub> = 0,85 · α<sub>v2</sub> · f<sub>cd</sub> = "
        f"<b>{biela['sigma_limite_MPa']:.2f} MPa</b>.<br/>"
        f"Aproveitamento: <b>{biela['razao'] * 100:.1f}%</b>."
    )
    blocos.append(Paragraph(verif, e["corpo"]))

    status_texto = (
        "✓ A biela ATENDE ao limite de tensão"
        if biela["ok"]
        else "✗ A biela ESTÁ ESMAGADA — revisar dimensões ou fck"
    )
    estilo_status = ParagraphStyle(
        "Status", parent=e["corpo"], fontSize=11,
        alignment=TA_CENTER, spaceBefore=8,
        textColor=COR_OK if biela["ok"] else COR_ERRO,
        fontName="Helvetica-Bold",
    )
    blocos.append(Paragraph(status_texto, estilo_status))

    # ===== 7. Diagrama esquematico (segunda pagina) =====
    blocos.append(PageBreak())
    blocos.append(Paragraph("7. DIAGRAMA ESQUEMÁTICO", e["secao"]))

    fig = desenhar_consolo(dados, resultado)
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
    img_buffer.seek(0)
    plt.close(fig)
    img = Image(img_buffer, width=16 * cm, height=11 * cm)
    blocos.append(img)

    # ===== Rodape =====
    blocos.append(Spacer(1, 1 * cm))
    blocos.append(Paragraph(
        "Memorial gerado pelo ConsoloCalc — ferramenta open-source para "
        "dimensionamento de consolos curtos de concreto armado "
        "conforme NBR 6118:2023.",
        e["rodape"],
    ))
    blocos.append(Paragraph(
        "consolocalc.streamlit.app  |  github.com/jpesssam-eng/consolocalc",
        e["rodape"],
    ))

    doc.build(blocos)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
