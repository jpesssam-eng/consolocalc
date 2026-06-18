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

import pandas as pd
import streamlit as st

from consolo_calc import DadosConsolo, dimensionar
from exportar import gerar_csv, gerar_excel
from memorial_pdf import gerar_pdf
from sensibilidade import (
    gerar_serie,
    grafico_aproveitamento_biela,
    grafico_armaduras,
    grafico_forcas,
    tabela_parametrica,
    _intervalo_padrao,
)
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
    "de bielas e tirantes."
)

fig_diagrama = desenhar_consolo(dados, r)
st.pyplot(fig_diagrama, use_container_width=True)


# ============================================================
# Downloads
# ============================================================
st.divider()
st.subheader("7. Downloads e exportacao")
st.markdown(
    "Baixe os resultados em diferentes formatos. O **PDF** e o memorial de "
    "calculo formatado, pronto para anexar a projetos. O **Excel** contem "
    "tres abas (entrada, resultados e memorial textual), pronto para Power BI "
    "ou Google Sheets. O **CSV** e o formato mais simples, util para analises "
    "rapidas em qualquer ferramenta."
)

ts = datetime.now().strftime("%Y%m%d_%H%M")

col_pdf, col_xlsx, col_csv = st.columns(3)
with col_pdf:
    st.download_button(
        label="📄 Memorial PDF",
        data=gerar_pdf(dados, r),
        file_name=f"memorial_consolocalc_{ts}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )
    st.caption("Relatorio formatado A4 com diagrama")

with col_xlsx:
    st.download_button(
        label="📊 Planilha Excel",
        data=gerar_excel(dados, r),
        file_name=f"consolocalc_{ts}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.caption("3 abas: entrada, resultados, memorial")

with col_csv:
    st.download_button(
        label="📋 CSV simples",
        data=gerar_csv(dados, r),
        file_name=f"consolocalc_{ts}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("Formato universal para analises")


# ============================================================
# Analise de sensibilidade - NOVO
# ============================================================
st.divider()
st.subheader("8. Analise de sensibilidade")
st.markdown(
    "Estude como os resultados variam ao alterar um unico parametro, "
    "mantendo os demais fixos. Util para identificar quais variaveis "
    "tem maior impacto no dimensionamento e para realizar **analises "
    "parametricas comparativas** entre cenarios."
)

# Parametro a variar
parametros_disponiveis = {
    "a (distancia da carga)": ("a", "cm"),
    "h (altura)": ("h", "cm"),
    "b (largura)": ("b", "cm"),
    "fck (concreto)": ("fck", "MPa"),
    "Vk (forca vertical)": ("Vk", "kN"),
    "Hk (forca horizontal)": ("Hk", "kN"),
    "d' (cobrimento)": ("d_linha", "cm"),
}

col_param, col_inicio, col_fim, col_passo = st.columns([2, 1, 1, 1])

with col_param:
    label_escolhido = st.selectbox(
        "Parametro a variar:",
        list(parametros_disponiveis.keys()),
        index=0,
    )
    nome_param, unidade_param = parametros_disponiveis[label_escolhido]
    valor_atual = getattr(dados, nome_param)
    inicio_padrao, fim_padrao, passo_padrao = _intervalo_padrao(
        nome_param, float(valor_atual)
    )

with col_inicio:
    inicio = st.number_input(
        f"Inicio ({unidade_param})",
        value=float(round(inicio_padrao, 2)),
        step=float(passo_padrao),
        key="ini",
    )
with col_fim:
    fim = st.number_input(
        f"Fim ({unidade_param})",
        value=float(round(fim_padrao, 2)),
        step=float(passo_padrao),
        key="fim",
    )
with col_passo:
    passo = st.number_input(
        f"Passo ({unidade_param})",
        value=float(round(passo_padrao, 2)),
        min_value=0.1,
        step=0.5,
        key="passo",
    )

if inicio >= fim:
    st.warning("O valor inicial deve ser menor que o final.")
elif (fim - inicio) / passo > 200:
    st.warning("Intervalo muito amplo ou passo muito pequeno. "
               "Aumente o passo ou reduza o intervalo.")
else:
    serie = gerar_serie(dados, nome_param, inicio, fim, passo)

    if not serie:
        st.warning("Nenhum ponto valido foi gerado neste intervalo. "
                   "Os consolos podem ter sido classificados como 'longo'.")
    else:
        # Tres graficos lado a lado em abas
        tab_arm, tab_biela, tab_forcas, tab_dados = st.tabs([
            "📈 Armaduras",
            "🛡️ Aproveitamento da biela",
            "💪 Forcas (Rsd e Fc)",
            "📋 Tabela parametrica",
        ])

        with tab_arm:
            st.plotly_chart(
                grafico_armaduras(serie, label_escolhido, unidade_param),
                use_container_width=True,
            )
            st.caption(
                "Variacao de A_s do tirante principal e da armadura de costura "
                "em funcao do parametro selecionado. Quanto maior a inclinacao "
                "da curva, mais sensivel o resultado a esse parametro."
            )

        with tab_biela:
            st.plotly_chart(
                grafico_aproveitamento_biela(serie, label_escolhido,
                                             unidade_param),
                use_container_width=True,
            )
            st.caption(
                "Aproveitamento da biela comprimida em relacao ao limite. "
                "Verde: regiao segura. Amarelo: alerta (80-100%). "
                "Vermelho: ruptura por esmagamento (>100%)."
            )

        with tab_forcas:
            st.plotly_chart(
                grafico_forcas(serie, label_escolhido, unidade_param),
                use_container_width=True,
            )
            st.caption(
                "Forcas atuantes no modelo de bielas e tirantes. "
                "R_sd e a tracao no tirante; F_c e a compressao na biela."
            )

        with tab_dados:
            tabela = tabela_parametrica(serie)
            df = pd.DataFrame(tabela)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv_param = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Baixar tabela parametrica (CSV)",
                data=csv_param,
                file_name=f"analise_param_{nome_param}_{ts}.csv",
                mime="text/csv",
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
