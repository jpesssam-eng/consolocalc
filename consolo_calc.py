"""
ConsoloCalc - Modulo de calculo
================================
Dimensionamento de consolos curtos de concreto armado pelo modelo de
bielas e tirantes de SANTOS (2021, cap. 6), com resistencias de bielas
e nos conforme a NBR 6118 e armaduras minimas conforme a NBR 9062:2017.

Modelo principal (Santos, 2021, Fig. 6.2):
    a1  = Vd / (b * fcd1)                      largura do no A    (Eq. 6.1)
    e   = (Hd / Vd) * d'                       excentricidade
    a   = a1/2 + ac + e                        distancia de calculo
    y   = d - sqrt(d^2 - 2*a1*a)               altura do no A     (Eq. 6.6)
    z   = d - y/2                              braco de alavanca
    cotg(theta) = y / a1 = a / z               (Eq. 6.5)
    Ftd = Vd * cotg(theta) + Hd                forca no tirante   (Eq. 6.4)
    x/d = (y / lambda) / d <= 0,4              ductilidade        (Eq. 6.7)

Dois metodos de calculo de z sao oferecidos:
    - "santos"       : z = d - y/2, com y pelo equilibrio do no A (rigoroso)
    - "simplificado" : z = 0,85 d, mantidos a e Hd do modelo (estimativa)

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
"""

import math
from dataclasses import dataclass


# ============================================================
# Coeficientes de ponderacao
# ============================================================
GAMMA_C = 1.4    # minoracao da resistencia do concreto
GAMMA_S = 1.15   # minoracao da resistencia do aco
GAMMA_F = 1.4    # majoracao das acoes (combinacao normal)

METODOS = ("santos", "simplificado")
_ALIAS = {"iterativo": "santos", "rigoroso": "santos"}


@dataclass(frozen=True)
class DadosConsolo:
    """
    Dados de entrada de um consolo curto.

        fck  : resistencia caracteristica do concreto (MPa)
        fyk  : resistencia caracteristica do aco (MPa)
        Vk   : forca vertical caracteristica (kN)
        Hk   : forca horizontal caracteristica (kN)
        a    : distancia da carga a face do pilar, ac (cm)
        h    : altura do consolo na face do pilar (cm)
        b    : largura do consolo (cm)
        d_linha : distancia do CG do tirante a face superior (cm)
        impedimento_horizontal : True se ha impedimento ao deslocamento
                                 horizontal (adota Hd >= 0,2 Vd, NBR 9062)
    """
    fck: float
    fyk: float
    Vk: float
    Hk: float
    a: float
    h: float
    b: float
    d_linha: float
    impedimento_horizontal: bool = False


def classificar_consolo(a: float, d: float) -> str:
    """Classificacao pela relacao ac/d (NBR 9062:2017; Santos, 2021)."""
    razao = a / d
    if razao <= 0.5:
        return "muito curto"
    elif razao <= 1.0:
        return "curto"
    return "longo"


def calcular_esforcos_de_calculo(dados: DadosConsolo) -> tuple:
    """Vd e Hd (kN). Com impedimento horizontal, Hd >= 0,2 Vd."""
    Vd = GAMMA_F * dados.Vk
    Hd = GAMMA_F * dados.Hk
    if dados.impedimento_horizontal:
        Hd = max(Hd, 0.2 * Vd)
    return Vd, Hd


def calcular_excentricidade(Hd: float, Vd: float, d_linha: float) -> float:
    """e = (Hd / Vd) * d'  (Santos, 2021)."""
    if Vd <= 0:
        return 0.0
    return (Hd / Vd) * d_linha


def resistencias_concreto(fck: float) -> dict:
    """fcd, alpha_v2, fcd1 (no CCC) e fcd3 (no CCT), em MPa."""
    fcd = fck / GAMMA_C
    av2 = 1 - fck / 250
    return {"fcd": fcd, "alpha_v2": av2,
            "fcd1": 0.85 * av2 * fcd, "fcd3": 0.72 * av2 * fcd}


def _lambda(fck: float) -> float:
    return 0.8 if fck <= 50 else 0.8 - (fck - 50) / 400


def modelo_santos(dados: DadosConsolo, Vd: float, Hd: float, d: float) -> dict:
    """
    Geometria do modelo principal de Santos (2021): no A pseudo-hidrostatico
    com tensao fcd1. Retorna a1, a (calculo), y, z, cotg(theta), x/d e se a
    solucao existe (d^2 >= 2*a1*a; caso contrario a biela nao cabe na secao).
    """
    res = resistencias_concreto(dados.fck)
    fcd1_kncm2 = res["fcd1"] / 10.0
    e = calcular_excentricidade(Hd, Vd, dados.d_linha)
    a1 = Vd / (dados.b * fcd1_kncm2)
    a_calc = a1 / 2 + dados.a + e
    disc = d * d - 2 * a1 * a_calc
    viavel = disc >= 0
    y = d - math.sqrt(disc) if viavel else d
    z = d - y / 2
    cotg = a_calc / z
    x = y / _lambda(dados.fck)
    return {"a1": a1, "a_calc": a_calc, "e": e, "y": y, "z": z,
            "cotg": cotg, "x": x, "x_d": x / d, "viavel": viavel,
            "fcd1": res["fcd1"], "fcd3": res["fcd3"]}


def dimensionar_armadura_tirante(Rsd: float, fyk: float) -> float:
    """As = Rsd / fyd (cm2), Rsd em kN e fyd em MPa."""
    return Rsd / ((fyk / GAMMA_S) * 0.1)


def dimensionar_armadura_costura(Vd_cotg: float, fyk: float, tipo: str) -> float:
    """
    Armadura de costura minima (NBR 9062:2017, conforme Santos, 2021):
        Ash,min = 0,4 * Vd*cotg(theta)/fyd   (0,5 < ac/d <= 1)
        Ash,min = 0,5 * Vd*cotg(theta)/fyd   (ac/d <= 0,5)
    """
    fator = 0.50 if tipo == "muito curto" else 0.40
    return fator * Vd_cotg / ((fyk / GAMMA_S) * 0.1)


def dimensionar(dados: DadosConsolo, metodo: str = "santos") -> dict:
    """
    Executa o dimensionamento.

    metodo: "santos" (rigoroso, z = d - y/2) ou "simplificado" (z = 0,85 d).
            "iterativo" e aceito como sinonimo de "santos".
    """
    metodo = _ALIAS.get(metodo, metodo)
    if metodo not in METODOS:
        raise ValueError(f"metodo invalido: {metodo}")

    d = dados.h - dados.d_linha
    Vd, Hd = calcular_esforcos_de_calculo(dados)
    tipo = classificar_consolo(dados.a, d)
    m = modelo_santos(dados, Vd, Hd, d)

    if metodo == "santos":
        z = m["z"]
    else:
        z = 0.85 * d
    cotg = m["a_calc"] / z

    theta = math.atan(1 / cotg)
    Vd_cotg = Vd * cotg
    Rsd = Vd_cotg + Hd                       # Eq. 6.4
    Fc = Vd / math.sin(theta)                # forca na biela inclinada
    As_tir = dimensionar_armadura_tirante(Rsd, dados.fyk)
    As_cost = dimensionar_armadura_costura(Vd_cotg, dados.fyk, tipo)

    # Verificacoes (Santos, 2021): existencia do no A com tensao fcd1 e
    # ductilidade x/d <= 0,4; angulo entre biela e tirante (NBR 6118:
    # 0,5 <= cotg(theta) <= 1,73, isto e, 30 a 63,4 graus)
    ductil_ok = m["viavel"] and m["x_d"] <= 0.4
    angulo_ok = 0.5 <= cotg <= 1 / math.tan(math.radians(30))
    verif = {
        "sigma_atuante_MPa": m["fcd1"],
        "sigma_limite_MPa": m["fcd1"],
        "x_d": m["x_d"],
        "x_d_limite": 0.4,
        "razao": (m["x_d"] / 0.4) if m["viavel"] else 9.99,
        "viavel": m["viavel"],
        "ok": ductil_ok,
        "angulo_ok": angulo_ok,
    }

    return {
        "d": d,
        "razao_ad": dados.a / d,
        "tipo": tipo,
        "Vd": Vd,
        "Hd": Hd,
        "e": m["e"],
        "a1": m["a1"],
        "a_calc": m["a_calc"],
        "y": m["y"],
        "z": z,
        "x": m["x"],
        "theta_rad": theta,
        "theta_deg": math.degrees(theta),
        "cotg": cotg,
        "Rsd": Rsd,
        "Fc": Fc,
        "As_tirante": As_tir,
        "As_costura": As_cost,
        "metodo": metodo,
        "iteracoes": 0,
        "convergiu": True,
        "biela": verif,
    }
