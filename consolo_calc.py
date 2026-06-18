"""
ConsoloCalc - Modulo de calculo
================================
Funcoes puras para dimensionamento de consolos curtos de concreto armado
conforme NBR 6118:2023, pelo metodo de bielas e tirantes.

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026

Este modulo NAO contem interface grafica. Apenas funcoes de calculo,
para que possam ser testadas, reutilizadas e citadas no TCC.
"""

import math
from dataclasses import dataclass


# ============================================================
# Coeficientes de ponderacao - NBR 6118:2023
# ============================================================
GAMMA_C = 1.4    # minoracao da resistencia do concreto
GAMMA_S = 1.15   # minoracao da resistencia do aco
GAMMA_F = 1.4    # majoracao das acoes (combinacao normal)


@dataclass
class DadosConsolo:
    """
    Estrutura com os dados de entrada de um consolo curto.

    Atributos:
        fck  : resistencia caracteristica do concreto (MPa)
        fyk  : resistencia caracteristica do aco (MPa) - 500 para CA-50
        Vk   : forca vertical caracteristica (kN)
        Hk   : forca horizontal caracteristica (kN)
        a    : distancia da carga a face do pilar (cm)
        h    : altura total do consolo (cm)
        b    : largura do consolo (cm)
        d_linha : distancia do CG da armadura ate a face tracionada (cm)
        impedimento_horizontal : True se o consolo restringe deslocamento
                                  horizontal (NBR 9062 exige Hd >= 0.2*Vd)
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
    """
    Classifica o consolo segundo a relacao a/d (NBR 6118:2023).

    - a/d <= 0,5         : consolo muito curto
    - 0,5 < a/d <= 1,0   : consolo curto
    - a/d > 1,0          : consolo longo (calcular como viga em balanco)
    """
    razao = a / d
    if razao <= 0.5:
        return "muito curto"
    elif razao <= 1.0:
        return "curto"
    else:
        return "longo"


def calcular_esforcos_de_calculo(dados: DadosConsolo) -> tuple:
    """
    Calcula os esforcos de calculo Vd e Hd a partir dos caracteristicos.

    Retorna (Vd, Hd) em kN.

    Se houver impedimento de deslocamento horizontal, aplica-se o
    minimo de Hd = 0,2 * Vd conforme NBR 9062.
    """
    Vd = GAMMA_F * dados.Vk
    Hd = GAMMA_F * dados.Hk
    if dados.impedimento_horizontal:
        Hd = max(Hd, 0.2 * Vd)
    return Vd, Hd


def calcular_excentricidade(Hd: float, Vd: float, d_linha: float) -> float:
    """
    Excentricidade da forca vertical em relacao ao eixo do tirante.

    e = (Hd / Vd) * d'
    """
    if Vd <= 0:
        return 0.0
    return (Hd / Vd) * d_linha


def calcular_forcas_no_modelo(dados: DadosConsolo, Vd: float, Hd: float,
                              d: float, e: float) -> dict:
    """
    Calcula as forcas no tirante (Rsd) e na biela comprimida (Fc)
    pelo equilibrio de momentos do modelo de bielas e tirantes.

    Adota-se inicialmente z = 0,85 * d (aproximacao classica).
    """
    z = 0.85 * d

    # Forca de tracao no tirante (equilibrio de momentos no no inferior)
    Rsd = (Vd * dados.a / z) + Hd * (dados.d_linha + e) / z

    # Angulo da biela com a horizontal
    theta = math.atan(z / dados.a)

    # Forca de compressao na biela (equilibrio no no superior)
    Fc = (Vd + Hd * e / z) / math.sin(theta)

    return {"z": z, "theta": theta, "Rsd": Rsd, "Fc": Fc}


def dimensionar_armadura_tirante(Rsd: float, fyk: float) -> float:
    """
    Area de aco do tirante principal.

    As = Rsd / fyd

    Rsd em kN, fyd em MPa, resultado em cm^2.
    """
    fyd = fyk / GAMMA_S
    # conversao: kN / (MPa * 0,1) = cm^2
    return Rsd / (fyd * 0.1)


def dimensionar_armadura_costura(As_tirante: float, tipo: str) -> float:
    """
    Area de aco da armadura de costura (estribos horizontais).

    NBR 6118:2023:
      - consolo curto       -> >= 0,40 * As_tirante
      - consolo muito curto -> >= 0,50 * As_tirante
    """
    fator = 0.50 if tipo == "muito curto" else 0.40
    return fator * As_tirante


def verificar_biela(Fc: float, b: float, h: float, fck: float,
                    theta: float) -> dict:
    """
    Verifica se a tensao na biela comprimida nao excede o limite.

    sigma_lim = 0,85 * alpha_v2 * fcd
    onde alpha_v2 = 1 - fck/250
    """
    fcd = fck / GAMMA_C                  # MPa
    alpha_v2 = 1 - fck / 250
    sigma_lim = 0.85 * alpha_v2 * fcd    # MPa

    # Aproximacao da area da biela (projecao da regiao comprimida)
    # Largura b x altura da regiao comprimida (estimativa ~ 0.2*h)
    x_biela = 0.2 * h
    A_biela = b * x_biela                # cm^2
    # Fc em kN, area em cm^2 -> sigma em kN/cm^2 -> *10 = MPa
    sigma = (Fc * 10) / A_biela if A_biela > 0 else float("inf")

    return {
        "sigma_atuante_MPa": sigma,
        "sigma_limite_MPa": sigma_lim,
        "razao": sigma / sigma_lim if sigma_lim > 0 else float("inf"),
        "ok": sigma <= sigma_lim
    }


def dimensionar(dados: DadosConsolo) -> dict:
    """
    Funcao principal: recebe os dados de entrada e retorna o
    dicionario completo com todos os resultados do dimensionamento.
    """
    # Geometria efetiva
    d = dados.h - dados.d_linha

    # Esforcos de calculo
    Vd, Hd = calcular_esforcos_de_calculo(dados)

    # Classificacao
    tipo = classificar_consolo(dados.a, d)

    # Excentricidade
    e = calcular_excentricidade(Hd, Vd, dados.d_linha)

    # Forcas no modelo
    forcas = calcular_forcas_no_modelo(dados, Vd, Hd, d, e)

    # Armaduras
    As_tir = dimensionar_armadura_tirante(forcas["Rsd"], dados.fyk)
    As_cost = dimensionar_armadura_costura(As_tir, tipo)

    # Verificacao da biela
    verif = verificar_biela(forcas["Fc"], dados.b, dados.h,
                            dados.fck, forcas["theta"])

    return {
        "d": d,
        "razao_ad": dados.a / d,
        "tipo": tipo,
        "Vd": Vd,
        "Hd": Hd,
        "e": e,
        "z": forcas["z"],
        "theta_rad": forcas["theta"],
        "theta_deg": math.degrees(forcas["theta"]),
        "Rsd": forcas["Rsd"],
        "Fc": forcas["Fc"],
        "As_tirante": As_tir,
        "As_costura": As_cost,
        "biela": verif,
    }
