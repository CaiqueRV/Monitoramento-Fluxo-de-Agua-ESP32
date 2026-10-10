"""Verifica a montagem na protoboard de 400 pontos a partir da lista de conexões informada."""
import re
parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b): parent[find(a)] = find(b)

def hole(ref):
    """'J3' -> nó da coluna 3 (F-J); 'E6' -> nó da coluna 6 (A-E); 'NEG'/'POS' -> trilhos."""
    if ref in ("NEG", "POS"): return ref
    m = re.fullmatch(r"([A-J])(\d+)", ref); r, c = m.group(1), int(m.group(2))
    return f"col{c}{'AE' if r in 'ABCDE' else 'FJ'}"

# ---- pinos plugados na protoboard --------------------------------------
esp = {"3V3":"J1","GND":"J2","D15":"J3","D2":"J4","D4":"J5","RX2":"J6","TX2":"J7","D5":"J8",
       "D18":"J9","D19":"J10","D21":"J11","RX0":"J12","TX0":"J13","D22":"J14","D23":"J15"}
oled = {"GND":"G28","VDD":"G27","SCK":"G26","SDA":"G25"}
jsn  = {"GND":"A25","TX":"A24","RX":"A23","5V":"A22"}
yf   = {"VERMELHO":"POS","PRETO":"NEG","AMARELO":"E2"}
leds = {"LED1":"A9","LED2":"A10","LED3":"A11"}          # anodos; catodos no trilho negativo
# ---- jumpers -------------------------------------------------------------
jumpers = [("I1","F27"),("I2","NEG"),("I8","E6"),("I4","B23"),("I5","E13"),("I14","F26"),
           ("I15","F25"),("F28","NEG"),("B25","NEG"),("B22","POS")]
for a,b in jumpers: union(hole(a),hole(b))
# VIN (outro lado do ESP32) -> trilho positivo
esp_vin = "ESP:VIN"; union(esp_vin,"POS")
# LEDs: catodo no trilho negativo
# ---- resistores (dois terminais, NÃO unem os nós) -------------------------
res = [("2k2","E6","G1"),("2k2","NEG","C13"),("1k","D2","D6"),("1k","C9","H9"),
       ("1k","C10","H10"),("1k","C11","H11"),("1k","D13","D24")]

def net_of(ref): return find(hole(ref))
pins = {}
for n,r in esp.items(): pins[f"ESP32.{n}"] = net_of(r)
pins["ESP32.VIN"] = find(esp_vin)
for n,r in oled.items(): pins[f"OLED.{n}"] = net_of(r)
for n,r in jsn.items(): pins[f"JSN.{n}"] = net_of(r)
for n,r in yf.items(): pins[f"YF-S201.{n}"] = net_of(r)
for n,r in leds.items():
    pins[f"{n}.anodo"] = net_of(r); pins[f"{n}.catodo"] = find("NEG")
nets = {}
for p,n in pins.items(): nets.setdefault(n,[]).append(p)
if __name__ == "__main__":
    print("NÓS COM MAIS DE UM PINO LIGADO (por fios/jumpers):\n")
    for n,ps in nets.items():
        if len(ps) > 1: print(f"  [{n}]  " + ", ".join(ps))
    print("\nPINOS SEM NENHUMA LIGAÇÃO DIRETA (sozinhos no nó):")
    print("  " + ", ".join(p for n,ps in nets.items() if len(ps)==1 for p in ps if p.startswith("ESP32")))
    print("\nRESISTORES (nó A  --R--  nó B), com os pinos presentes em cada nó:")
    for v,a,b in res:
        na,nb = net_of(a),net_of(b)
        print(f"  {v:>3}  {a:>3} --- {b:<3}  | {a}: {nets.get(na,[hole(a)])} | {b}: {nets.get(nb,[hole(b)])}")

# ---- conferência automática com os pinos definidos no firmware ------------------
def conferir_firmware(caminho_main):
    import os
    src = open(caminho_main, encoding="utf-8").read()
    gp = {m.group(1): int(m.group(2)) for m in re.finditer(r"#define\s+(\w+)\s+(\d+)\b", src)}
    def esp_net(n): return pins.get(f"ESP32.D{n}")
    def via_res(net_a, pino_b):
        nb = pins[pino_b]
        return any({net_of(a), net_of(b)} == {net_a, nb} for _, a, b in res)
    regras = [
        ("OLED_SDA",     lambda n: esp_net(n) == pins["OLED.SDA"],           "ligação direta ao SDA do OLED"),
        ("OLED_SCL",     lambda n: esp_net(n) == pins["OLED.SCK"],           "ligação direta ao SCK do OLED"),
        ("JSN_RX",       lambda n: esp_net(n) == pins["JSN.RX"],             "ligação direta ao RX (trigger) do JSN"),
        ("JSN_TX",       lambda n: via_res(esp_net(n), "JSN.TX"),            "via 1 kΩ do divisor ao TX (eco) do JSN"),
        ("FLUXO_PIN",    lambda n: via_res(esp_net(n), "YF-S201.AMARELO"),   "via 1 kΩ em série ao fio amarelo do YF-S201"),
        ("FLUXO_PIN",    lambda n: via_res(esp_net(n), "ESP32.3V3"),         "pull-up de 2,2 kΩ ao 3V3"),
        ("LED_VERDE",    lambda n: via_res(esp_net(n), "LED1.anodo"),        "via 1 kΩ ao LED 1"),
        ("LED_AMARELO",  lambda n: via_res(esp_net(n), "LED2.anodo"),        "via 1 kΩ ao LED 2"),
        ("LED_VERMELHO", lambda n: via_res(esp_net(n), "LED3.anodo"),        "via 1 kΩ ao LED 3"),
    ]
    print(f"\nCONFERÊNCIA COM O FIRMWARE ({os.path.relpath(caminho_main)}):")
    falhas = 0
    for nome, teste, desc in regras:
        n = gp[nome]; ok = esp_net(n) is not None and teste(n)
        falhas += not ok
        print(f"  {'OK   ' if ok else 'FALHA'} {nome:<13} = GPIO{n:<3} {desc}")
    print("  Resultado:", "todas as ligações conferem." if not falhas else f"{falhas} divergência(s).")
    return falhas

if __name__ == "__main__":
    import os, sys
    main_cpp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main.cpp")
    sys.exit(1 if conferir_firmware(main_cpp) else 0)
