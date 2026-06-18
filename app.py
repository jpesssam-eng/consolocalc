"""
ConsoloCalc - Interface web (Streamlit)
========================================
Aplicacao para dimensionamento de consolos curtos de concreto armado
conforme NBR 6118:2023, pelo metodo de bielas e tirantes.

Para executar:
    streamlit run app.py

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

from datetime import datetime

import streamlit as st

from consolo_calc import DadosConsolo, dimensionar
from memorial_pdf import gerar_pdf
from visualizacao import desenhar_consolo


# ============================================================
# Configuracao da pagina
# ============================================================
st.set_page_config(
    page_title="ConsoloCalc",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ ConsoloCalc")
st.markdown(
    "**Dimensionamento de consolos curtos de concreto armado**  \n"
    "Metodo de bielas e tirantes • NBR 6118:2023"
)
st.divider()


# ============================================================
# Entrada de dados (sidebar)
# ============================================================
st.sidebar.header("Dados de entrada")

st.sidebar.subheader("Materiais")
fck = st.sidebar.number_input(
    "fck — concreto (MPa)",
    min_value=20.0, max_value=90.0, value=25.0, step=5.0
)
fyk = st.sidebar.number_input(
    "fyk — aco (MPa)",
    min_value=250.0, max_value=600.0, value=500.0, step=50.0,
    help="CA-50 → 500 MPa | CA-25 → 250 MPa"
)

st.sidebar.subheader("Geometria (cm)")
a = st.sidebar.number_input("a — distancia da carga a face do pilar",
                            min_value=1.0, value=20.0, step=1.0)
h = st.sidebar.number_input("h — altura total do consolo",
                            min_value=10.0, value=40.0, step=1.0)
b = st.sidebar.number_input("b — largura do consolo",
                            min_value=10.0, value=20.0, step=1.0)
d_linha = st.sidebar.number_input("d' — cobrimento ate CG da armadura",
                                  min_value=2.0, value=4.0, step=0.5)

st.sidebar.subheader("Esforcos (kN)")
Vk = st.sidebar.number_input("Vk — forca vertical",
                             min_value=0.0, value=100.0, step=10.0)
Hk = st.sidebar.number_input("Hk — forca horizontal",
                             min_value=0.0, value=0.0, step=10.0)

impedimento = st.sidebar.checkbox(
    "Impedimento de deslocamento horizontal",
    help="Se marcado, Hd minimo = 0,2 * Vd (NBR 9062)"
)


# ============================================================
# Execucao do calculo
# ============================================================
dados = DadosConsolo(
    fck=fck, fyk=fyk, Vk=Vk, Hk=Hk,
    a=a, h=h, b=b, d_linha=d_linha,
    impedimento_horizontal=impedimento
)
r = dimensionar(dados)


# ============================================================
# Apresentacao dos resultados
# ============================================================
col1, col2 = st.columns([1, 1])

# ---- Coluna 1: classificacao e forcas ----
with col1:
    st.subheader("1. Classificacao do consolo")
    st.write(f"d = h − d' = {dados.h:.1f} − {dados.d_linha:.1f} = **{r['d']:.1f} cm**")
    st.write(f"Relacao a/d = {dados.a:.1f} / {r['d']:.1f} = **{r['razao_ad']:.3f}**")
    st.info(f"Tipo: **consolo {r['tipo']}**")

    if r["tipo"] == "longo":
        st.error("⚠️ Consolo longo deve ser dimensionado como viga em balanco. "
                 "Este modelo nao se aplica.")
        st.stop()

    st.subheader("2. Esforcos de calculo")
    st.write(f"Vd = γf · Vk = 1,4 · {dados.Vk:.1f} = **{r['Vd']:.2f} kN**")
    st.write(f"Hd = **{r['Hd']:.2f} kN**")
    st.write(f"Excentricidade e = (Hd/Vd) · d' = **{r['e']:.3f} cm**")

    st.subheader("3. Modelo de bielas e tirantes")
    st.write(f"Braco de alavanca z = 0,85 · d = **{r['z']:.2f} cm**")
    st.write(f"Angulo da biela θ = **{r['theta_deg']:.2f}°**")
    st.write(f"Forca no tirante Rsd = **{r['Rsd']:.2f} kN**")
    st.write(f"Forca na biela Fc = **{r['Fc']:.2f} kN**")

# ---- Coluna 2: armaduras e verificacoes ----
with col2:
    st.subheader("4. Armaduras calculadas")
    st.metric("Tirante principal — As", f"{r['As_tirante']:.2f} cm²")
    st.metric("Costura — As,cost",      f"{r['As_costura']:.2f} cm²")

    st.subheader("5. Verificacao da biela comprimida")
    biela = r["biela"]
    st.write(f"σ atuante = **{biela['sigma_atuante_MPa']:.2f} MPa**")
    st.write(f"σ limite  = **{biela['sigma_limite_MPa']:.2f} MPa**")
    st.write(f"Aproveitamento = **{biela['razao']*100:.1f}%**")

    if biela["ok"]:
        st.success("✅ Biela comprimida — OK")
    else:
        st.error("❌ Biela comprimida ESMAGADA — aumentar secao ou fck")


# ============================================================
# Visualizacao grafica
# ============================================================
st.divider()
st.subheader("6. Diagrama esquematico do consolo")
st.markdown(
    "Representacao grafica da geometria, da carga aplicada e do modelo "
    "de bielas e tirantes. As cotas e o angulo da biela sao atualizados "
    "automaticamente conforme os dados de entrada."
)

fig = desenhar_consolo(dados, r)
st.pyplot(fig, use_container_width=True)


# ============================================================
# Download do memorial em PDF - NOVO
# ============================================================
st.divider()
st.subheader("7. Memorial de calculo")
st.markdown(
    "Baixe o memorial em PDF formatado, com todos os dados de entrada, "
    "calculos, resultados e o diagrama esquematico. O documento "
    "pode ser arquivado no projeto, anexado a relatorios ou impresso."
)

col_a, col_b = st.columns([1, 2])
with col_a:
    pdf_bytes = gerar_pdf(dados, r)
    nome_arquivo = (
        f"memorial_consolocalc_"
        f"{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    st.download_button(
        label="📄 Baixar memorial em PDF",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
with col_b:
    st.caption(
        "O arquivo gerado contem 2 paginas: dados, calculos e verificacoes "
        "na primeira, e o diagrama esquematico na segunda. "
        "Pronto para impressao em A4."
    )


# ============================================================
# Rodape
# ============================================================
st.divider()
st.caption(
    "Ferramenta desenvolvida como parte do Trabalho de Conclusao de Curso "
    "do Centro Universitario Internacional UNINTER. "
    "Conforme ABNT NBR 6118:2023. "
    "Codigo aberto disponivel no GitHub."
)
