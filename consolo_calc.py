"""
ConsoloCalc - Modulo de calculo (versao refinada)
==================================================
Funcoes para dimensionamento de consolos curtos de concreto armado
conforme NBR 6118:2023, pelo metodo de bielas e tirantes.

Esta versao implementa o calculo ITERATIVO do braco de alavanca z,
mais rigoroso que a aproximacao simplificada z = 0,85 * d, e suporta
dois modos de calculo selecionaveis pelo usuario:

    - "simplificado": z = 0,85 * d (estimativa classica, conservadora)
    - "iterativo":    z = d - 0,4 * x (atualizado iterativamente
                       a partir do equilibrio interno da secao)

Esse design permite a comparacao entre metodos no proprio TCC,
agregando valor academico ao trabalho.

Autor: Junior Pessoa da Silva
TCC - Engenharia Civil - UNINTER - 2026
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
    Calcula Vd e Hd a partir dos esforcos caracteristicos.

    Retorna (Vd, Hd) em kN.

    Se houver impedimento de deslocamento horizontal, aplica-se
    Hd minimo = 0,2 * Vd conforme NBR 9062.
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


def _calcular_z_simplificado(d: float) -> dict:
    """
    Metodo simplificado: z = 0,85 * d.
    Estimativa conservadora classica, sem iteracao.
    """
    return {"z": 0.85 * d, "x": None, "iteracoes": 0,
            "convergiu": True, "metodo": "simplificado"}


def _calcular_z_iterativo(dados: DadosConsolo, Vd: float, Hd: float,
                          d: float, e: float,
                          tol: float = 0.01, max_iter: int = 50) -> dict:
    """
    Calculo iterativo de z baseado no equilibrio interno da secao.

    Algoritmo:
        1. Estimativa inicial z = 0,85 * d
        2. Calcular Rsd = (Vd*a + Hd*(d'+e)) / z
        3. Determinar a profundidade da linha neutra x
           pelo equilibrio horizontal de forcas:
           As * fyd = 0,85 * fcd * b * x
           portanto x = Rsd / (0,85 * fcd * b)
        4. Atualizar z_novo = d - 0,4 * x
        5. Repetir ate convergir

    Retorna dicionario com z, x, iteracoes e flag de convergencia.
    """
    fcd = dados.fck / GAMMA_C        # MPa
    fcd_kncm2 = fcd / 10.0           # kN/cm² (1 MPa = 0,1 kN/cm²)

    z = 0.85 * d  # estimativa inicial
    x = 0.0
    iteracao = 0
    convergiu = False

    for iteracao in range(1, max_iter + 1):
        Rsd = (Vd * dados.a / z) + Hd * (dados.d_linha + e) / z
        # Equilibrio horizontal: Rsd = 0,85 * fcd * b * x
        x = Rsd / (0.85 * fcd_kncm2 * dados.b)
        # Limite fisico: x nao pode exceder d
        x = min(x, 0.95 * d)
        z_novo = d - 0.4 * x

        if abs(z_novo - z) < tol:
            z = z_novo
            convergiu = True
            break
        z = z_novo

    return {
        "z": z, "x": x, "iteracoes": iteracao,
        "convergiu": convergiu, "metodo": "iterativo"
    }


def calcular_forcas_no_modelo(dados: DadosConsolo, Vd: float, Hd: float,
                              d: float, e: float, metodo: str = "iterativo") -> dict:
    """
    Calcula as forcas no tirante (Rsd) e na biela comprimida (Fc)
    pelo equilibrio do modelo de bielas e tirantes.

    Parametros:
        metodo: "simplificado" (z = 0,85d) ou "iterativo" (z = d - 0,4x).
    """
    if metodo == "simplificado":
        info_z = _calcular_z_simplificado(d)
    else:
        info_z = _calcular_z_iterativo(dados, Vd, Hd, d, e)

    z = info_z["z"]

    # Forca de tracao no tirante (equilibrio de momentos)
    Rsd = (Vd * dados.a / z) + Hd * (dados.d_linha + e) / z

    # Angulo da biela com a horizontal
    theta = math.atan(z / dados.a)

    # Forca de compressao na biela (equilibrio no no superior)
    Fc = (Vd + Hd * e / z) / math.sin(theta)

    return {
        "z": z, "x": info_z["x"], "theta": theta,
        "Rsd": Rsd, "Fc": Fc, "iteracoes": info_z["iteracoes"],
        "convergiu": info_z["convergiu"], "metodo": info_z["metodo"]
    }


def dimensionar_armadura_tirante(Rsd: float, fyk: float) -> float:
    """
    Area de aco do tirante principal.

    As = Rsd / fyd

    Rsd em kN, fyd em MPa, resultado em cm^2.
    """
    fyd = fyk / GAMMA_S
    return Rsd / (fyd * 0.1)  # kN / (MPa * 0,1) = cm^2


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

    # Aproximacao da area da biela
    x_biela = 0.2 * h
    A_biela = b * x_biela                # cm^2
    sigma = (Fc * 10) / A_biela if A_biela > 0 else float("inf")

    return {
        "sigma_atuante_MPa": sigma,
        "sigma_limite_MPa": sigma_lim,
        "razao": sigma / sigma_lim if sigma_lim > 0 else float("inf"),
        "ok": sigma <= sigma_lim
    }


def dimensionar(dados: DadosConsolo, metodo: str = "iterativo") -> dict:
    """
    Funcao principal: recebe os dados de entrada e o metodo de calculo
    de z, e retorna o dicionario completo com todos os resultados.

    Parametros:
        dados  : DadosConsolo com os dados de entrada
        metodo : "simplificado" (z = 0,85d) ou "iterativo" (padrao)
    """
    d = dados.h - dados.d_linha
    Vd, Hd = calcular_esforcos_de_calculo(dados)
    tipo = classificar_consolo(dados.a, d)
    e = calcular_excentricidade(Hd, Vd, dados.d_linha)
    forcas = calcular_forcas_no_modelo(dados, Vd, Hd, d, e, metodo)
    As_tir = dimensionar_armadura_tirante(forcas["Rsd"], dados.fyk)
    As_cost = dimensionar_armadura_costura(As_tir, tipo)
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
        "x": forcas["x"],
        "theta_rad": forcas["theta"],
        "theta_deg": math.degrees(forcas["theta"]),
        "Rsd": forcas["Rsd"],
        "Fc": forcas["Fc"],
        "As_tirante": As_tir,
        "As_costura": As_cost,
        "metodo": forcas["metodo"],
        "iteracoes": forcas["iteracoes"],
        "convergiu": forcas["convergiu"],
        "biela": verif,
    }
