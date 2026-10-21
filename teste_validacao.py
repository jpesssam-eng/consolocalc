"""
ConsoloCalc - Teste de validacao
=================================
Compara os resultados da ferramenta com exemplos resolvidos da
literatura tecnica.

Para executar:
    python teste_validacao.py

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

from consolo_calc import DadosConsolo, dimensionar

GAMMA_F = 1.4

CASOS = [
    {
        "fonte": "Santos (2021), Boxe 6.2 - Exemplo 2",
        "descricao": ("C35, CA-50; Vd = 800 kN; Hd = 160 kN; ac = 20 cm; "
                      "d = 37,5 cm; d' = 7,5 cm; b = 45 cm."),
        "dados": DadosConsolo(fck=35.0, fyk=500.0,
                              Vk=800.0 / GAMMA_F, Hk=160.0 / GAMMA_F,
                              a=20.0, h=45.0, b=45.0, d_linha=7.5),
        "referencia": {"z": 33.69, "Rsd": 784.0, "As_tirante": 18.0,
                       "As_costura": 5.74},
    },
    {
        "fonte": "Silva e Giongo (2000, ex. 6.1, apud Siqueira, 2018)",
        "descricao": ("C20, CA-50; Fk = 610 kN; ac = 58 cm; h = 80 cm; "
                      "b = 80 cm; d' = 2,5 cm; Hd = 0,2 Vd (NBR 9062, adotado)."),
        "dados": DadosConsolo(fck=20.0, fyk=500.0, Vk=610.0, Hk=0.0,
                              a=58.0, h=80.0, b=80.0, d_linha=2.5,
                              impedimento_horizontal=True),
        "referencia": {"Rsd": 875.2, "As_tirante": 20.2, "As_costura": 6.91},
    },
]


def dif(v, ref):
    return f"{(v - ref) / ref * 100:+.1f}%" if ref else "n/d"


def imprimir_caso(caso):
    print("=" * 72)
    print(f"  {caso['fonte']}")
    print(f"  {caso['descricao']}")
    print("-" * 72)
    ref = caso["referencia"]
    rs = dimensionar(caso["dados"], "santos")
    rp = dimensionar(caso["dados"], "simplificado")
    print(f"  {'Variavel':<20}{'Simplificado':>13}{'Rigoroso':>13}"
          f"{'Referencia':>13}{'Dif. rig.':>11}")
    for chave, nome in (("z", "z (cm)"), ("Rsd", "Rsd (kN)"),
                        ("As_tirante", "As tirante (cm2)"),
                        ("As_costura", "As costura (cm2)")):
        r_ref = ref.get(chave)
        ref_txt = f"{r_ref:.2f}" if r_ref else "-"
        print(f"  {nome:<20}{rp[chave]:>13.2f}{rs[chave]:>13.2f}"
              f"{ref_txt:>13}{dif(rs[chave], r_ref) if r_ref else '-':>11}")
    b = rs["biela"]
    print(f"  Tipo: {rs['tipo']} (ac/d = {rs['razao_ad']:.2f}); "
          f"x/d = {b['x_d']:.2f} ({'OK' if b['ok'] else 'NAO ATENDE'})")
    print()


if __name__ == "__main__":
    for caso in CASOS:
        imprimir_caso(caso)
