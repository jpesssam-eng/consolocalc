"""
ConsoloCalc - Teste de validacao
=================================
Script que executa o Exemplo 1 do Araujo (2014, vol. 4, p. 122),
tambem utilizado por Siqueira (2018) como caso de validacao.

Para executar:
    python teste_validacao.py
"""

from consolo_calc import DadosConsolo, dimensionar


def caso_araujo_2014():
    """
    Exemplo 1 (Araujo, 2014, vol. 4, p. 122):
      Vk = 100 kN aplicada na face superior
      Pilar quadrado 20 x 20 cm
      a  = 60 cm (distancia da carga a face do pilar)
      C25 (fck = 25 MPa) | CA-50 (fyk = 500 MPa)
      Resultado de referencia: As,tirante ≈ 2,42 cm² | As,costura ≈ 1,21 cm²
    """
    dados = DadosConsolo(
        fck=25.0,
        fyk=500.0,
        Vk=100.0,
        Hk=0.0,
        a=60.0,
        h=72.0,        # adotado h = 1,2 * a (estimativa usual)
        b=20.0,
        d_linha=4.0,
        impedimento_horizontal=False
    )
    return dados


def imprimir_resultados(dados, r):
    print("=" * 60)
    print("  CONSOLO CALC — TESTE DE VALIDACAO")
    print("  Exemplo 1 — Araujo (2014, vol. 4, p. 122)")
    print("=" * 60)
    print(f"  Dados:")
    print(f"    Vk = {dados.Vk} kN | Hk = {dados.Hk} kN")
    print(f"    a = {dados.a} cm | h = {dados.h} cm | b = {dados.b} cm")
    print(f"    fck = {dados.fck} MPa | fyk = {dados.fyk} MPa")
    print(f"    d' = {dados.d_linha} cm")
    print("-" * 60)
    print(f"  Classificacao : consolo {r['tipo']} (a/d = {r['razao_ad']:.3f})")
    print(f"  Vd = {r['Vd']:.2f} kN | Hd = {r['Hd']:.2f} kN")
    print(f"  z = {r['z']:.2f} cm | theta = {r['theta_deg']:.2f}°")
    print(f"  Rsd = {r['Rsd']:.2f} kN | Fc = {r['Fc']:.2f} kN")
    print("-" * 60)
    print(f"  As,tirante = {r['As_tirante']:.2f} cm²")
    print(f"    Referencia (Araujo, 2014) = 2,42 cm²")
    diff = abs(r['As_tirante'] - 2.42) / 2.42 * 100
    print(f"    Diferenca = {diff:.1f}%")
    print()
    print(f"  As,costura = {r['As_costura']:.2f} cm²")
    print(f"    Referencia (Araujo, 2014) = 1,21 cm²")
    diff2 = abs(r['As_costura'] - 1.21) / 1.21 * 100
    print(f"    Diferenca = {diff2:.1f}%")
    print("-" * 60)
    biela = r["biela"]
    status = "OK" if biela["ok"] else "ESMAGADA"
    print(f"  Biela: {status} ({biela['razao']*100:.1f}% de aproveitamento)")
    print("=" * 60)


if __name__ == "__main__":
    dados = caso_araujo_2014()
    resultado = dimensionar(dados)
    imprimir_resultados(dados, resultado)
