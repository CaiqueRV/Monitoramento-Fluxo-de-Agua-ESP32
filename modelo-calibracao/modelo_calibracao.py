#!/usr/bin/env python3
"""
Modelo de calibração - Sensor de rios (ESP32)

Reproduz em Python, linha a linha, as contas feitas pelo firmware em
projeto-fisico-sensor-rios/src/main.cpp, para permitir:
  * conferir os valores esperados antes de gravar no ESP32;
  * simular diferentes calibrações (alturas, pulsos por litro);
  * gerar as tabelas usadas em analise-calculos-sensores.md.

Uso:
    python3 modelo_calibracao.py              # imprime as tabelas
    python3 modelo_calibracao.py --dist 25.4  # nível para uma distância
    python3 modelo_calibracao.py --pulsos 120 # vazão para 120 pulsos em 2 s
"""
import argparse

# ---- Constantes (iguais às do main.cpp) ------------------------------------
DISTANCIA_VAZIO_CM = 30.0     # reservatório VAZIO  -> 0 %
DISTANCIA_CHEIO_CM = 20.0     # reservatório CHEIO  -> 100 %
DIST_MIN_VALIDA_CM = 20.0     # leitura abaixo disso é descartada
DIST_MAX_VALIDA_CM = 600.0    # leitura acima disso é descartada
VELOCIDADE_SOM_CM_US = 0.0343  # 343 m/s (~20 °C)
PULSOS_POR_LITRO = 450.0      # YF-S201: F(Hz) = 7,5 * Q(L/min)
JANELA_VAZAO_S = 2.0          # TEMPO_VAZAO = 2000 ms
LIMITE_ATENCAO = 33.0         # %
LIMITE_PERIGO = 66.0          # %


def distancia_cm(duracao_echo_us):
    """duracao * 0,0343 / 2 (ida e volta do som). None = leitura inválida."""
    if duracao_echo_us == 0:
        return None
    d = duracao_echo_us * VELOCIDADE_SOM_CM_US / 2.0
    if d < DIST_MIN_VALIDA_CM or d > DIST_MAX_VALIDA_CM:
        return None
    return d


def nivel_percentual(d_cm):
    """Interpolação linear entre VAZIO (0 %) e CHEIO (100 %), saturada."""
    if d_cm >= DISTANCIA_VAZIO_CM:
        return 0.0
    if d_cm <= DISTANCIA_CHEIO_CM:
        return 100.0
    n = (DISTANCIA_VAZIO_CM - d_cm) / (DISTANCIA_VAZIO_CM - DISTANCIA_CHEIO_CM) * 100.0
    return max(0.0, min(100.0, n))


def status(nivel):
    """Mesma lógica de atualizarStatus(): <33 NORMAL, 33..66 ATENCAO, >66 PERIGO."""
    if nivel < LIMITE_ATENCAO:
        return "NORMAL (LED verde)"
    if nivel <= LIMITE_PERIGO:
        return "ATENCAO (LED amarelo)"
    return "PERIGO (LED vermelho)"


def vazao_l_min(pulsos, janela_s=JANELA_VAZAO_S):
    """(pulsos / 450) = litros na janela;  * (60 / janela) = L/min."""
    return (pulsos / PULSOS_POR_LITRO) * (60.0 / janela_s)


def tabelas():
    print("Tempo de eco (us) -> distância (cm)")
    for us in (1100, 1167, 1458, 1749, 2000, 3500):
        d = distancia_cm(us)
        txt = f"{d:7.2f} cm" if d is not None else "invalida (descartada)"
        print(f"  {us:5d} us -> {txt}")

    print("\nDistância (cm) -> nível (%) -> status")
    for d in (30, 28, 26.7, 25, 23.4, 22, 20):
        n = nivel_percentual(d)
        print(f"  {d:5.1f} cm -> {n:6.1f} %  {status(n)}")

    print("\nPulsos em 2 s -> vazão (L/min)")
    for p in (0, 1, 15, 30, 75, 150, 300, 450):
        print(f"  {p:4d} pulsos -> {vazao_l_min(p):7.3f} L/min")

    print(f"\nResolução do nível : {100 / (DISTANCIA_VAZIO_CM - DISTANCIA_CHEIO_CM):.1f} % por cm")
    print(f"Resolução da vazão : {vazao_l_min(1):.4f} L/min por pulso (janela de {JANELA_VAZAO_S:.0f} s)")
    print(f"Volume por pulso   : {1000 / PULSOS_POR_LITRO:.2f} mL")
    print(f"Distância p/ 33 %  : {DISTANCIA_VAZIO_CM - 0.33 * (DISTANCIA_VAZIO_CM - DISTANCIA_CHEIO_CM):.2f} cm")
    print(f"Distância p/ 66 %  : {DISTANCIA_VAZIO_CM - 0.66 * (DISTANCIA_VAZIO_CM - DISTANCIA_CHEIO_CM):.2f} cm")

    print("\nEfeito da temperatura na velocidade do som (v = 331,3 + 0,606*T m/s)")
    for t in (10, 20, 30, 40):
        v = 331.3 + 0.606 * t
        erro = (v / 343.0 - 1) * 100
        print(f"  {t:2d} C -> {v:6.1f} m/s ({erro:+.1f} % vs 343 m/s)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", type=float, help="distância medida (cm)")
    ap.add_argument("--pulsos", type=int, help="pulsos contados em uma janela")
    a = ap.parse_args()
    if a.dist is None and a.pulsos is None:
        tabelas()
    if a.dist is not None:
        n = nivel_percentual(a.dist)
        print(f"{a.dist:.1f} cm -> {n:.1f} % -> {status(n)}")
    if a.pulsos is not None:
        print(f"{a.pulsos} pulsos em {JANELA_VAZAO_S:.0f} s -> {vazao_l_min(a.pulsos):.3f} L/min")
