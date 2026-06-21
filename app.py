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
from pacote_completo import gerar_pacote_zip
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


# ============================================================
# Funcoes com cache (otimizacao de performance)
# ============================================================
@st.cache_data(show_spinner=False)
def _calculo_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo):
    """Executa o dimensionamento e retorna o resultado em cache."""
    dados = DadosConsolo(
        fck=fck, fyk=fyk, Vk=Vk, Hk=Hk, a=a, h=h, b=b,
        d_linha=d_linha, impedimento_horizontal=imp,
    )
    r = dimensionar(dados, metodo=metodo)
    return dados, r


@st.cache_data(show_spinner=False)
def _pdf_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo):
    """Gera o PDF do memorial em cache."""
    dados, r = _calculo_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo)
    return gerar_pdf(dados, r)


@st.cache_data(show_spinner=False)
def _excel_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo):
    """Gera a planilha Excel em cache."""
    dados, r = _calculo_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo)
    return gerar_excel(dados, r)


@st.cache_data(show_spinner=False)
def _csv_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo):
    """Gera o CSV em cache."""
    dados, r = _calculo_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo)
    return gerar_csv(dados, r)


@st.cache_data(show_spinner="Gerando pacote completo...")
def _zip_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo):
    """Gera o pacote ZIP em cache."""
    dados, r = _calculo_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, imp, metodo)
    return gerar_pacote_zip(dados, r, metodo=metodo)


st.title("🏗️ ConsoloCalc")
st.markdown(
    "**Dimensionamento de consolos curtos de concreto armado**  \n"
    "Metodo de bielas e tirantes • NBR 6118:2023"
)

# ============================================================
# Sobre a ferramenta (expansor recolhido por padrao)
# ============================================================
with st.expander("📘 Sobre a ferramenta e instrucoes de uso"):
    tab_sobre, tab_metodo, tab_uso, tab_normas, tab_lim = st.tabs([
        "🎯 Sobre",
        "📐 Metodologia",
        "📖 Como usar",
        "📚 Normas",
        "⚠️ Limitacoes",
    ])

    with tab_sobre:
        st.markdown(
            "**ConsoloCalc** e uma aplicacao web de codigo aberto para o "
            "dimensionamento de consolos curtos de concreto armado segundo "
            "a NBR 6118:2023, pelo metodo de bielas e tirantes.\n\n"
            "Foi desenvolvida como Trabalho de Conclusao de Curso "
            "(TCC) do Centro Universitario Internacional UNINTER, "
            "como contribuicao a democratizacao do acesso a ferramentas "
            "de calculo estrutural no Brasil.\n\n"
            "**Caracteristicas principais:**\n"
            "- Aplicacao web acessivel por qualquer navegador, sem instalacao\n"
            "- Implementa dois metodos de calculo: simplificado e iterativo\n"
            "- Gera memorial em PDF, planilha Excel e CSV para integracao com "
            "Power BI ou Google Sheets\n"
            "- Inclui analise de sensibilidade interativa com graficos\n"
            "- Codigo-fonte publico sob licenca MIT\n\n"
            "**Links:**\n"
            "- Aplicacao publica: https://consolocalc.streamlit.app\n"
            "- Codigo-fonte: https://github.com/jpesssam-eng/consolocalc"
        )

    with tab_metodo:
        st.markdown(
            "**Metodo de bielas e tirantes** modela o consolo como uma "
            "trelica idealizada composta por:\n\n"
            "- **Biela comprimida**: campo diagonal de compressao no concreto, "
            "do ponto de aplicacao da carga ate a base do consolo\n"
            "- **Tirante tracionado**: campo horizontal de tracao, absorvido "
            "pela armadura principal proxima a face superior\n"
            "- **Nos**: regioes de transferencia das forcas\n\n"
            "**Equacoes principais (NBR 6118:2023, item 22.3):**\n\n"
            "- Forca no tirante: Rsd = (Vd · a)/z + Hd · (d' + e)/z\n"
            "- Forca na biela: Fc = (Vd + Hd · e/z) / sin(θ)\n"
            "- Tensao limite na biela: σRd = 0,85 · αv2 · fcd, "
            "com αv2 = 1 − fck/250\n\n"
            "**Calculo do braco de alavanca z**:\n"
            "- *Simplificado*: z = 0,85 · d (estimativa conservadora)\n"
            "- *Iterativo*: z = d − 0,4·x (atualizado iterativamente "
            "pelo equilibrio interno; converge em 3-5 iteracoes)\n\n"
            "**Armadura de costura**: 0,40 · As,tirante para consolos curtos, "
            "0,50 · As,tirante para consolos muito curtos."
        )

    with tab_uso:
        st.markdown(
            "**Passo a passo:**\n\n"
            "1. Preencher os dados de entrada na **barra lateral** (materiais, "
            "geometria, esforcos)\n"
            "2. Escolher o **metodo de calculo do braco z** (recomendado: "
            "iterativo)\n"
            "3. Visualizar resultados em tempo real nas secoes 1 a 5\n"
            "4. Conferir o **diagrama esquematico** na secao 6\n"
            "5. **Baixar resultados** na secao 7 (pacote ZIP completo "
            "recomendado)\n"
            "6. Explorar a **analise de sensibilidade** interativa na "
            "secao 8 para entender o impacto de cada parametro\n\n"
            "**Dica:** passe o mouse sobre cada campo na sidebar para ver "
            "tooltips explicativos com o significado fisico do parametro."
        )

    with tab_normas:
        st.markdown(
            "**Normas tecnicas aplicaveis:**\n\n"
            "- **ABNT NBR 6118:2023** — Projeto de estruturas de concreto: "
            "norma base para o calculo, define o metodo de bielas e tirantes "
            "para regioes D (descontinuidades) no item 22.3.\n"
            "- **ABNT NBR 9062:2017** — Projeto e execucao de estruturas de "
            "concreto pre-moldado: aplicavel a consolos em estruturas pre-"
            "fabricadas; exige Hd minima = 0,2·Vd quando ha impedimento ao "
            "deslocamento horizontal.\n"
            "- **ABNT NBR 6023:2018** — Referencias bibliograficas: "
            "formatacao das citacoes neste TCC.\n\n"
            "**Referencias teoricas:**\n\n"
            "- ARAUJO (2014). Curso de Concreto Armado, vol. 4.\n"
            "- EL DEBS (2017). Concreto pre-moldado: fundamentos e aplicacoes.\n"
            "- SANTOS (2021). Projeto estrutural por bielas e tirantes.\n"
            "- SCHLAICH, SCHAFER e JENNEWEIN (1987). Toward a consistent "
            "design of structural concrete. PCI Journal, v.32, n.3.\n"
            "- SILVA e GIONGO (2000). Modelos de bielas e tirantes aplicados "
            "a estruturas de concreto armado. EESC-USP."
        )

    with tab_lim:
        st.markdown(
            "**Escopo atendido:**\n\n"
            "- Consolos curtos (0,5 < a/d ≤ 1,0) e muito curtos (a/d ≤ 0,5)\n"
            "- Concretos convencionais (classes C20 a C90)\n"
            "- Acos CA-25, CA-50 e CA-60\n"
            "- Cargas vertical e horizontal estaticas\n\n"
            "**Nao contemplado:**\n\n"
            "- Consolos longos (devem ser dimensionados como vigas em balanco)\n"
            "- Detalhamento de barras (numero, diametro, ancoragem)\n"
            "- Geracao de desenhos em DXF/AutoCAD\n"
            "- Verificacao a fadiga ou acoes sismicas\n"
            "- Concretos especiais (com fibras, autoadensavel, UHPC)\n"
            "- Integracao direta com softwares comerciais (TQS, Eberick)\n\n"
            "Estas limitacoes orientam as sugestoes de trabalhos futuros "
            "apresentadas no TCC."
        )

st.divider()


# ============================================================
# Entrada de dados (sidebar)
# ============================================================
st.sidebar.header("Dados de entrada")

st.sidebar.subheader("Materiais")
fck = st.sidebar.number_input(
    "fck — concreto (MPa)",
    min_value=20.0, max_value=90.0, value=25.0, step=5.0,
    help=(
        "Resistencia caracteristica do concreto a compressao aos 28 dias. "
        "Classes usuais: C20, C25, C30, C40, C50 (concretos convencionais); "
        "C60-C90 (concretos de alto desempenho). A NBR 6118:2023 define "
        "essas classes e os criterios de uso. Em consolos curtos, o fck "
        "influencia principalmente a verificacao da biela comprimida."
    ),
)
fyk = st.sidebar.number_input(
    "fyk — aco (MPa)",
    min_value=250.0, max_value=600.0, value=500.0, step=50.0,
    help=(
        "Resistencia caracteristica do aco ao escoamento. "
        "CA-50 → 500 MPa (mais comum no Brasil) | "
        "CA-25 → 250 MPa (uso restrito a estribos finos) | "
        "CA-60 → 600 MPa (telas soldadas). "
        "Define a area de aco necessaria pela equacao As = Rsd / fyd."
    ),
)

st.sidebar.subheader("Geometria (cm)")
a = st.sidebar.number_input(
    "a — distancia da carga a face do pilar",
    min_value=1.0, value=20.0, step=1.0,
    help=(
        "Distancia horizontal entre o ponto de aplicacao da carga vertical "
        "e a face do pilar de apoio. Em consolos curtos, esta distancia "
        "determina a relacao a/d que classifica o consolo: "
        "a/d ≤ 0,5 → muito curto; 0,5 < a/d ≤ 1,0 → curto; "
        "a/d > 1,0 → longo (dimensionar como viga em balanco)."
    ),
)
h = st.sidebar.number_input(
    "h — altura total do consolo",
    min_value=10.0, value=40.0, step=1.0,
    help=(
        "Altura total da secao do consolo, medida do topo a base. "
        "Influencia diretamente o braco de alavanca z = d - 0,4x "
        "e o angulo da biela. Pratica usual em pre-fabricados: h ≈ 1,2 · a."
    ),
)
b = st.sidebar.number_input(
    "b — largura do consolo",
    min_value=10.0, value=20.0, step=1.0,
    help=(
        "Largura (espessura) do consolo, medida perpendicularmente ao plano "
        "do desenho. Geralmente coincide com a largura do pilar de apoio "
        "para garantir continuidade da biela comprimida. Influencia a "
        "verificacao da biela: σ = Fc / (b · 0,2·h)."
    ),
)
d_linha = st.sidebar.number_input(
    "d' — cobrimento ate CG da armadura",
    min_value=2.0, value=4.0, step=0.5,
    help=(
        "Distancia da face superior tracionada ate o centro de gravidade "
        "da armadura do tirante principal. Inclui o cobrimento nominal "
        "exigido pela NBR 6118:2023 (Tabela 7.2, classe de agressividade) "
        "mais metade do diametro das barras. Valor tipico: 3 a 5 cm."
    ),
)

st.sidebar.subheader("Esforcos (kN)")
Vk = st.sidebar.number_input(
    "Vk — forca vertical",
    min_value=0.0, value=100.0, step=10.0,
    help=(
        "Forca vertical caracteristica (valor sem majoracao) aplicada "
        "no consolo. Sera multiplicada por γf = 1,4 para obter Vd. "
        "Tipicamente, e a reacao de apoio da viga apoiada sobre o consolo."
    ),
)
Hk = st.sidebar.number_input(
    "Hk — forca horizontal",
    min_value=0.0, value=0.0, step=10.0,
    help=(
        "Forca horizontal caracteristica (valor sem majoracao). "
        "Causada por dilatacao termica, frenagem, retracao do concreto "
        "ou imperfeicoes geometricas. Aumenta a tracao no tirante e "
        "introduz excentricidade na carga vertical."
    ),
)

impedimento = st.sidebar.checkbox(
    "Impedimento de deslocamento horizontal",
    help=(
        "Marque se o consolo restringe o deslocamento horizontal do "
        "elemento apoiado (sem aparelho de neoprene livre). Nesse caso, "
        "a NBR 9062:2017 exige Hd minima = 0,2 · Vd, conservadoramente."
    ),
)

# ============================================================
# Seletor de metodo de calculo (sidebar)
# ============================================================
st.sidebar.divider()
st.sidebar.subheader("Metodo de calculo do braco z")
metodo = st.sidebar.radio(
    "Selecione o metodo:",
    options=["iterativo", "simplificado"],
    format_func=lambda x: {
        "iterativo": "Iterativo (z = d − 0,4·x)",
        "simplificado": "Simplificado (z = 0,85·d)",
    }[x],
    help=(
        "O metodo ITERATIVO atualiza z a partir do equilibrio interno "
        "da secao, aproximando-se mais dos valores de referencia da "
        "literatura. O metodo SIMPLIFICADO usa uma estimativa fixa, "
        "mais conservadora."
    ),
)


# ============================================================
# Execucao do calculo
# ============================================================
dados = DadosConsolo(
    fck=fck, fyk=fyk, Vk=Vk, Hk=Hk,
    a=a, h=h, b=b, d_linha=d_linha,
    impedimento_horizontal=impedimento
)
r = dimensionar(dados, metodo=metodo)


# ============================================================
# Indicador de metodo (topo do conteudo principal)
# ============================================================
col_metodo1, col_metodo2 = st.columns([3, 1])
with col_metodo1:
    if metodo == "iterativo":
        st.info(
            f"**Metodo iterativo**: z convergiu em "
            f"**{r['iteracoes']} iteracoes** "
            f"({'convergiu' if r['convergiu'] else 'nao convergiu'})."
        )
    else:
        st.warning(
            "**Metodo simplificado**: utilizando z = 0,85·d como estimativa fixa."
        )


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
    if metodo == "iterativo" and r["x"] is not None:
        st.write(f"Profundidade da linha neutra x = **{r['x']:.2f} cm**")
        st.write(f"Braco de alavanca z = d − 0,4·x = **{r['z']:.2f} cm**")
    else:
        st.write(f"Braco de alavanca z = 0,85·d = **{r['z']:.2f} cm**")
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
# Comparacao entre metodos (expansor)
# ============================================================
with st.expander("📊 Comparar os dois metodos (simplificado vs iterativo)"):
    r_simp = dimensionar(dados, metodo="simplificado")
    r_iter = dimensionar(dados, metodo="iterativo")

    comp_df = pd.DataFrame({
        "Variavel": ["z (cm)", "Rsd (kN)", "Fc (kN)",
                     "As tirante (cm²)", "As costura (cm²)",
                     "Aproveitamento biela (%)"],
        "Simplificado": [
            f"{r_simp['z']:.2f}", f"{r_simp['Rsd']:.2f}",
            f"{r_simp['Fc']:.2f}", f"{r_simp['As_tirante']:.3f}",
            f"{r_simp['As_costura']:.3f}",
            f"{r_simp['biela']['razao']*100:.1f}",
        ],
        "Iterativo": [
            f"{r_iter['z']:.2f}", f"{r_iter['Rsd']:.2f}",
            f"{r_iter['Fc']:.2f}", f"{r_iter['As_tirante']:.3f}",
            f"{r_iter['As_costura']:.3f}",
            f"{r_iter['biela']['razao']*100:.1f}",
        ],
        "Diferenca (%)": [
            f"{(r_iter['z']-r_simp['z'])/r_simp['z']*100:+.1f}",
            f"{(r_iter['Rsd']-r_simp['Rsd'])/r_simp['Rsd']*100:+.1f}",
            f"{(r_iter['Fc']-r_simp['Fc'])/r_simp['Fc']*100:+.1f}",
            f"{(r_iter['As_tirante']-r_simp['As_tirante'])/r_simp['As_tirante']*100:+.1f}",
            f"{(r_iter['As_costura']-r_simp['As_costura'])/r_simp['As_costura']*100:+.1f}",
            f"{(r_iter['biela']['razao']-r_simp['biela']['razao'])/r_simp['biela']['razao']*100:+.1f}",
        ],
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    st.caption(
        "O metodo iterativo produz valores menores de Rsd e As, pois leva em "
        "conta o real braco de alavanca da secao apos o equilibrio interno. "
        "O metodo simplificado e mais conservador, util como verificacao "
        "rapida de seguranca."
    )


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
    "Baixe os resultados em diferentes formatos. O **pacote completo (ZIP)** "
    "e a opcao recomendada e contem todos os arquivos de uma so vez. Os "
    "downloads individuais permitem obter apenas o formato desejado."
)

ts = datetime.now().strftime("%Y%m%d_%H%M")

# Botao destaque: PACOTE COMPLETO (ZIP)
st.download_button(
    label="📦 BAIXAR PACOTE COMPLETO (.zip)",
    data=_zip_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, impedimento, metodo),
    file_name=f"consolocalc_pacote_{ts}.zip",
    mime="application/zip",
    type="primary",
    use_container_width=True,
)
st.caption(
    "ZIP contendo: memorial PDF, planilha Excel, dados CSV, "
    "diagrama PNG, grafico de sensibilidade PNG e README com resumo."
)

st.markdown("**Ou baixe arquivos individuais:**")

col_pdf, col_xlsx, col_csv = st.columns(3)
with col_pdf:
    st.download_button(
        label="📄 Memorial PDF",
        data=_pdf_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, impedimento, metodo),
        file_name=f"memorial_consolocalc_{ts}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.caption("Relatorio formatado A4 com diagrama")

with col_xlsx:
    st.download_button(
        label="📊 Planilha Excel",
        data=_excel_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, impedimento, metodo),
        file_name=f"consolocalc_{ts}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.caption("3 abas: entrada, resultados, memorial")

with col_csv:
    st.download_button(
        label="📋 CSV simples",
        data=_csv_cached(fck, fyk, Vk, Hk, a, h, b, d_linha, impedimento, metodo),
        file_name=f"consolocalc_{ts}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("Formato universal para analises")


# ============================================================
# Analise de sensibilidade
# ============================================================
st.divider()
st.subheader("8. Analise de sensibilidade")
st.markdown(
    "Estude como os resultados variam ao alterar um unico parametro, "
    "mantendo os demais fixos. Util para identificar quais variaveis "
    "tem maior impacto no dimensionamento e para realizar **analises "
    "parametricas comparativas** entre cenarios."
)

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
    serie = gerar_serie(dados, nome_param, inicio, fim, passo, metodo=metodo)

    if not serie:
        st.warning("Nenhum ponto valido foi gerado neste intervalo. "
                   "Os consolos podem ter sido classificados como 'longo'.")
    else:
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
                "em funcao do parametro selecionado."
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
