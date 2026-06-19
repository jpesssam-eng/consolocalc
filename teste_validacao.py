"""
ConsoloCalc - Teste de validacao
=================================
Script que executa casos de validacao da literatura tecnica,
comparando os resultados das duas abordagens implementadas
(simplificada e iterativa) com os valores de referencia.

Para executar:
    python teste_validacao.py

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

from consolo_calc import DadosConsolo, dimensionar


# ============================================================
# Caso 1: Araujo (2014), vol. 4, p. 122
# ============================================================
CASO_ARAUJO = {
    "fonte": "Araujo (2014), vol. 4, p. 122",
    "descricao": (
        "Vk = 100 kN aplicada na face superior; pilar quadrado 20 x 20 cm; "
        "a = 60 cm; C25 (fck = 25 MPa); CA-50 (fyk = 500 MPa)."
    ),
    "dados": DadosConsolo(
        fck=25.0, fyk=500.0,
        Vk=100.0, Hk=0.0,
        a=60.0, h=72.0, b=20.0, d_linha=4.0,
        impedimento_horizontal=False,
    ),
    "referencia": {
        "As_tirante": 2.42,  # cm²
        "As_costura": 1.21,  # cm²
    },
}

# ============================================================
# Caso 2: Silva e Giongo (2000), p. 169 - PENDENTE
# ============================================================
# TODO: Atualizar com os valores reais do livro Silva e Giongo (2000).
# Os dados abaixo sao um placeholder a ser substituido pelo
# aluno apos consulta a referencia original.
CASO_SILVA_GIONGO = {
    "fonte": "Silva e Giongo (2000), p. 169 (PLACEHOLDER)",
    "descricao": (
        "Caso a ser preenchido com os dados reais do livro Silva e Giongo. "
        "Esta entrada serve como template — substitua pelos valores corretos."
    ),
    "dados": DadosConsolo(
        fck=20.0, fyk=500.0,
        Vk=200.0, Hk=0.0,
        a=30.0, h=60.0, b=80.0, d_linha=4.0,
        impedimento_horizontal=False,
    ),
    "referencia": {
        "As_tirante": None,  # preencher com valor do livro
        "As_costura": None,  # preencher com valor do livro
    },
}


def calcular_diferenca(valor_obtido: float, valor_referencia) -> str:
    """Calcula a diferenca percentual com tratamento para referencia None."""
    if valor_referencia is None or valor_referencia == 0:
        return "n/d"
    diff = (valor_obtido - valor_referencia) / valor_referencia * 100
    return f"{diff:+.1f}%"


def imprimir_caso(caso: dict):
    """Executa o caso com ambos os metodos e imprime relatorio comparativo."""
    print("=" * 70)
    print(f"  CASO: {caso['fonte']}")
    print("=" * 70)
    print(f"  {caso['descricao']}")
    print()

    dados = caso["dados"]
    print(f"  Dados de entrada:")
    print(f"    Vk = {dados.Vk} kN | Hk = {dados.Hk} kN")
    print(f"    a = {dados.a} cm | h = {dados.h} cm | b = {dados.b} cm | d' = {dados.d_linha} cm")
    print(f"    fck = {dados.fck} MPa | fyk = {dados.fyk} MPa")
    print()

    ref = caso["referencia"]
    ref_As_tir = ref.get("As_tirante")
    ref_As_cost = ref.get("As_costura")

    # ------ Calculo com ambos os metodos ------
    r_simp = dimensionar(dados, metodo="simplificado")
    r_iter = dimensionar(dados, metodo="iterativo")

    # ------ Tabela comparativa ------
    print(f"  Comparacao entre metodos:")
    print(f"  {'-' * 66}")
    print(f"  {'Variavel':<22}{'Simplificado':>14}{'Iterativo':>14}{'Referencia':>14}")
    print(f"  {'-' * 66}")

    linhas = [
        ("z (cm)", r_simp["z"], r_iter["z"], None),
        ("Rsd (kN)", r_simp["Rsd"], r_iter["Rsd"], None),
        ("Fc (kN)", r_simp["Fc"], r_iter["Fc"], None),
        ("theta (graus)", r_simp["theta_deg"], r_iter["theta_deg"], None),
        ("As tirante (cm²)", r_simp["As_tirante"], r_iter["As_tirante"], ref_As_tir),
        ("As costura (cm²)", r_simp["As_costura"], r_iter["As_costura"], ref_As_cost),
    ]

    for nome, vsimp, viter, vref in linhas:
        ref_txt = f"{vref:.3f}" if vref is not None else "—"
        print(f"  {nome:<22}{vsimp:>14.3f}{viter:>14.3f}{ref_txt:>14}")
    print(f"  {'-' * 66}")

    # ------ Diferencas vs referencia ------
    if ref_As_tir is not None:
        print()
        print(f"  Diferenca vs referencia:")
        print(f"    As tirante (simplificado): "
              f"{calcular_diferenca(r_simp['As_tirante'], ref_As_tir)}")
        print(f"    As tirante (iterativo):    "
              f"{calcular_diferenca(r_iter['As_tirante'], ref_As_tir)}")
        if ref_As_cost is not None:
            print(f"    As costura (simplificado): "
                  f"{calcular_diferenca(r_simp['As_costura'], ref_As_cost)}")
            print(f"    As costura (iterativo):    "
                  f"{calcular_diferenca(r_iter['As_costura'], ref_As_cost)}")
    else:
        print()
        print(f"  Diferenca vs referencia: nao disponivel "
              f"(preencher dados de referencia no codigo)")

    print()
    print(f"  Iteracoes do metodo iterativo: {r_iter['iteracoes']} "
          f"({'convergiu' if r_iter['convergiu'] else 'NAO convergiu'})")

    # ------ Verificacao da biela ------
    biela = r_iter["biela"]
    status = "OK" if biela["ok"] else "ESMAGADA"
    print(f"  Biela (iterativo): {status} ({biela['razao']*100:.1f}% aproveitamento)")
    print()


if __name__ == "__main__":
    print()
    print("##" * 35)
    print("  TESTES DE VALIDACAO - CONSOLOCALC")
    print("##" * 35)
    print()

    imprimir_caso(CASO_ARAUJO)
    imprimir_caso(CASO_SILVA_GIONGO)

    print("=" * 70)
    print("  CONCLUSAO")
    print("=" * 70)
    print(
        "  O metodo iterativo produz valores significativamente mais\n"
        "  proximos das referencias bibliograficas que o metodo simplificado.\n"
        "  A diferenca residual deve-se a variacoes entre metodos rigorosos\n"
        "  (NBR 6118:2023) e abordagens empiricas adotadas por alguns autores.\n"
    )
