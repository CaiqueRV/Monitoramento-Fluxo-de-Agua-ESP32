#!/usr/bin/env python3
"""
Gera diagrama-protoboard.svg: vista da protoboard de 400 pontos com TODAS as conexões
informadas (componentes, jumpers, resistores, LEDs e sensores).

Convenções da protoboard:
  * colunas 1-30; linhas A-E ligadas entre si em cada coluna, F-J ligadas entre si em cada coluna;
    as metades A-E e F-J são separadas pelo canal central;
  * um par de trilhos (negativo e positivo) abaixo da linha A.
"""
import math

P = 26                      # passo entre furos
X0 = 100                    # x da coluna 1
def X(c): return X0 + (c - 1) * P

ROW = {"J": 285, "I": 311, "H": 337, "G": 363, "F": 389,
       "E": 449, "D": 475, "C": 501, "B": 527, "A": 553}
NEG_Y, POS_Y = 608, 634
BOARD_TOP, BOARD_BOT = 262, 662
BOARD_L, BOARD_R = 60, 894
GAP_CH = [399, 407, 415, 423, 431, 439]       # canais no vão central para os jumpers
W, H = 980, 985

def hx(ref):                 # 'J3' -> (x, y)
    return X(int(ref[1:])), ROW[ref[0]]

RAIL_COLS = [c for g in range(5) for c in range(1 + g * 6, 6 + g * 6)]   # 1-5, 7-11, 13-17, 19-23, 25-29

out = []
add = out.append

def line(pts, color, w=3.2, halo=True, dash=None):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    if halo:
        add(f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w + 3}" stroke-linejoin="round" stroke-linecap="round"/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{ds}/>')

def dot(x, y, color, r=4.2):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="#222" stroke-width="1"/>')

def text(x, y, s, size=11, anchor="middle", weight="normal", fill="#222", rot=None, halo=False, family="DejaVu Sans, Arial, sans-serif"):
    t = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    h = ' stroke="#fff" stroke-width="3" paint-order="stroke"' if halo else ""
    add(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{fill}"{t}{h}>{s}</text>')

def resistor_body(x, y, ang, kohm, label):
    """Corpo de resistor centrado em (x,y), girado 'ang' graus."""
    bands = {"1k": ["#7b3f00", "#111", "#c1272d"], "2k2": ["#c1272d", "#c1272d", "#c1272d"]}[kohm]
    add(f'<g transform="translate({x},{y}) rotate({ang})">')
    add('<rect x="-17" y="-6.5" width="34" height="13" rx="6" fill="#e8d3a4" stroke="#8a6d3b" stroke-width="1.2"/>')
    for i, c in enumerate(bands):
        add(f'<rect x="{-10 + i * 8}" y="-6.5" width="3.4" height="13" fill="{c}"/>')
    add('<rect x="11" y="-6.5" width="3" height="13" fill="#d4af37"/>')
    add('</g>')

# --------------------------------------------------------------------------- fundo
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
text(W / 2, 30, "Sensor de rios — conexões na protoboard de 400 pontos", 20, weight="bold")
text(W / 2, 50, "Vista de cima. Colunas 1–30; em cada coluna, A–E estão ligados entre si e F–J estão ligados entre si (canal central isola as duas metades).", 11, fill="#555")

# --------------------------------------------------------------------------- protoboard
add(f'<rect x="{BOARD_L}" y="{BOARD_TOP}" width="{BOARD_R - BOARD_L}" height="{BOARD_BOT - BOARD_TOP}" rx="8" fill="#efe9dd" stroke="#b9ae97" stroke-width="2"/>')
add(f'<rect x="{BOARD_L + 6}" y="{(ROW["F"] + ROW["E"]) / 2 - 9}" width="{BOARD_R - BOARD_L - 12}" height="18" rx="3" fill="#d9d1bf"/>')
add(f'<line x1="{BOARD_L + 6}" x2="{BOARD_R - 6}" y1="{NEG_Y - 20}" y2="{NEG_Y - 20}" stroke="#d9d1bf" stroke-width="1"/>')
# furos
for r, y in ROW.items():
    for c in range(1, 31):
        add(f'<rect x="{X(c) - 3.2}" y="{y - 3.2}" width="6.4" height="6.4" rx="1" fill="#6e6a60"/>')
    text(BOARD_L + 14, y + 4, r, 11, weight="bold", fill="#555")
    text(BOARD_R - 14, y + 4, r, 11, weight="bold", fill="#555")
for c in range(1, 31):
    text(X(c), BOARD_TOP + 11, str(c), 9, fill="#666")
    text(X(c), BOARD_BOT - 3, str(c), 9, fill="#666")
for y, col, sign in ((NEG_Y, "#1f5fbf", "−"), (POS_Y, "#c1272d", "+")):
    add(f'<line x1="{BOARD_L + 30}" x2="{BOARD_R - 30}" y1="{y - 13}" y2="{y - 13}" stroke="{col}" stroke-width="1.5"/>')
    for c in RAIL_COLS:
        add(f'<rect x="{X(c) - 3.2}" y="{y - 3.2}" width="6.4" height="6.4" rx="1" fill="#6e6a60"/>')
    text(BOARD_L + 14, y + 6, sign, 17, weight="bold", fill=col)
    text(BOARD_R - 14, y + 6, sign, 17, weight="bold", fill=col)
text(BOARD_L + 14, NEG_Y - 20, "", 8)

# --------------------------------------------------------------------------- ESP32 (cabeçalho em J1–J15)
esp_pins = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19", "D21", "RX0", "TX0", "D22", "D23"]
bx0, bx1, by0, by1 = X(1) - 22, X(15) + 22, 70, 242
add(f'<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" rx="8" fill="#16202b" stroke="#0b0f14" stroke-width="2"/>')
add(f'<rect x="{(bx0 + bx1) / 2 - 38}" y="{by0 - 14}" width="76" height="30" rx="4" fill="#c9ccd1" stroke="#777"/>')
text((bx0 + bx1) / 2, by0 + 40, "ESP32 DEVKIT V1", 16, weight="bold", fill="#fff")
text((bx0 + bx1) / 2, by0 + 58, "pinos plugados em J1–J15", 10, fill="#9fb3c8")
add(f'<rect x="{(bx0 + bx1) / 2 - 42}" y="{by0 + 70}" width="84" height="46" rx="3" fill="#2b3a4a" stroke="#445"/>')
text((bx0 + bx1) / 2, by0 + 98, "ESP-WROOM-32", 9, fill="#9fb3c8")
for i, name in enumerate(esp_pins, start=1):
    x = X(i)
    add(f'<rect x="{x - 2.5}" y="{by1}" width="5" height="{ROW["J"] - by1}" fill="#d4af37"/>')
    text(x, by1 - 6, name, 10, anchor="start", weight="bold", fill="#fff", rot=-90)
# VIN (outro cabeçalho da placa)
vin = (bx0, 205)
add(f'<rect x="{bx0 - 8}" y="{vin[1] - 8}" width="10" height="16" fill="#d4af37"/>')
text(bx0 + 8, vin[1] + 4, "VIN", 10, anchor="start", weight="bold", fill="#fff")

# --------------------------------------------------------------------------- OLED (G25–G28)
ox0, ox1, oy0, oy1 = X(25) - 17, X(28) + 17, 112, 340
add(f'<rect x="{ox0}" y="{oy0}" width="{ox1 - ox0}" height="{oy1 - oy0}" rx="6" fill="#143a73" stroke="#0b2347" stroke-width="2"/>')
add(f'<rect x="{ox0 + 10}" y="{oy0 + 12}" width="{ox1 - ox0 - 20}" height="{(oy1 - oy0) * 0.55:.0f}" rx="3" fill="#05070a" stroke="#555"/>')
text((ox0 + ox1) / 2, oy0 + 60, "OLED", 12, weight="bold", fill="#7fd1ff")
text((ox0 + ox1) / 2, oy0 + 76, "SSD1306", 11, fill="#7fd1ff")
text((ox0 + ox1) / 2, oy0 + 92, "0,96\" I2C", 10, fill="#7fd1ff")
for c, nm in ((25, "SDA"), (26, "SCK"), (27, "VDD"), (28, "GND")):
    x = X(c)
    add(f'<rect x="{x - 2.5}" y="{oy1}" width="5" height="{ROW["G"] - oy1}" fill="#d4af37"/>')
    text(x, oy1 - 8, nm, 10, anchor="start", weight="bold", fill="#fff", rot=-90)

# --------------------------------------------------------------------------- JSN-SR04M-2 (A22–A25) sobre os trilhos
jx0, jx1, jy0, jy1 = X(22) - 9, X(25) + 12, ROW["A"] + 17, ROW["A"] + 86
add(f'<rect x="{jx0}" y="{jy0}" width="{jx1 - jx0}" height="{jy1 - jy0}" rx="5" fill="#1b5e20" stroke="#0d3a12" stroke-width="2"/>')
text((jx0 + jx1) / 2, jy0 + 28, "JSN-SR04M-2", 11, weight="bold", fill="#fff")
text((jx0 + jx1) / 2, jy0 + 43, "módulo", 9, fill="#c8e6c9")
for c, nm in ((22, "5V"), (23, "RX"), (24, "TX"), (25, "GND")):
    x = X(c)
    add(f'<rect x="{x - 2.5}" y="{ROW["A"]}" width="5" height="{jy0 - ROW["A"]}" fill="#d4af37"/>')
    text(x, jy0 + 13, nm, 9, weight="bold", fill="#fff")
# cabo + transdutor
cx = (jx0 + jx1) / 2
add(f'<path d="M{cx},{jy1} C{cx},{jy1 + 30} {cx + 40},{jy1 + 25} {cx + 60},{jy1 + 50}" fill="none" stroke="#222" stroke-width="4"/>')
add(f'<circle cx="{cx + 75}" cy="{jy1 + 62}" r="22" fill="#2f3b45" stroke="#111" stroke-width="2"/>')
add(f'<circle cx="{cx + 75}" cy="{jy1 + 62}" r="12" fill="#6b7a86"/>')
text(cx + 104, jy1 + 66, "sonda", 10, anchor="start", fill="#444")

# --------------------------------------------------------------------------- LEDs (anodo A9–A11, catodo no trilho −)
leds = [(9, "#2e9e44", "LED 1 (verde)", "GPIO18"), (10, "#f2c200", "LED 2 (amarelo)", "GPIO19"), (11, "#d62828", "LED 3 (vermelho)", "GPIO21")]
for c, col, nm, gp in leds:
    x = X(c)
    line([(x, ROW["A"]), (x, 563)], "#777", 2, halo=False)         # perna anodo
    line([(x, 585), (x, NEG_Y)], "#777", 2, halo=False)            # perna catodo
    add(f'<circle cx="{x}" cy="574" r="11" fill="{col}" stroke="#222" stroke-width="1.5"/>')
    add(f'<path d="M{x - 7},{574} a7,7 0 0 1 7,-7" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/>')
    dot(x, NEG_Y, "#1f5fbf", 3.5)
text(X(10), BOARD_BOT + 16, "LEDs: cores assumidas (1 verde, 2 amarelo, 3 vermelho)", 9, fill="#666")

# --------------------------------------------------------------------------- resistores
# 1 kΩ  D2–D6  e  D13–D24 (pernas sobem ao canal entre as linhas E e D, corpo no canal)
CH = (ROW["E"] + ROW["D"]) / 2
for a, b, ref in ((2, 6, "D2–D6"), (13, 24, "D13–D24")):
    line([(X(a), ROW["D"]), (X(a), CH), (X(b), CH), (X(b), ROW["D"])], "#8a8a8a", 2, halo=False)
    resistor_body((X(a) + X(b)) / 2, CH, 0, "1k", ref)
    dot(X(a), ROW["D"], "#555", 3.5); dot(X(b), ROW["D"], "#555", 3.5)
text((X(2) + X(6)) / 2, CH - 12, "1 kΩ", 10, weight="bold", halo=True)
text((X(13) + X(24)) / 2, CH - 12, "1 kΩ", 10, weight="bold", halo=True)
# 1 kΩ dos LEDs (C→H, atravessam o canal central)
for c in (9, 10, 11):
    x = X(c)
    line([(x, ROW["C"]), (x, ROW["H"])], "#8a8a8a", 2, halo=False)
    resistor_body(x, 356, 90, "1k", "")
    dot(x, ROW["C"], "#555", 3.5); dot(x, ROW["H"], "#555", 3.5)
text(X(11) + 18, 326, "1 kΩ × 3", 10, anchor="start", weight="bold", halo=True)
# 2,2 kΩ  C6→−  e  C13→−
line([(X(13), ROW["C"]), (X(13), NEG_Y)], "#8a8a8a", 2, halo=False)
resistor_body(X(13), 548, 90, "2k2", "")
dot(X(13), ROW["C"], "#555", 3.5); dot(X(13), NEG_Y, "#1f5fbf", 3.5)
text(X(13) + 18, 556, "2,2 kΩ", 10, anchor="start", weight="bold", halo=True)

# --------------------------------------------------------------------------- jumpers
C_GND, C_5V, C_3V3 = "#111111", "#d62828", "#ef7d00"
def jmp(pts, color, a, b):
    line(pts, color)
    dot(*pts[0], color); dot(*pts[-1], color)

# canais do vão central (de cima para baixo)
ch = dict(zip(["I15F25", "I14F26", "I1F27", "I8E6", "I5E13", "I4B23"], GAP_CH))
# I1 -> F27  (3V3 -> OLED VDD)
jmp([hx("I1"), (X(1), ch["I1F27"]), (X(27), ch["I1F27"]), hx("F27")], C_3V3, "I1", "F27")
# I2 -> trilho − (GND ESP32)
jmp([hx("I2"), (X(2), 324), (46, 324), (46, NEG_Y), (X(1), NEG_Y)], C_GND, "I2", "NEG")
# I8 -> E6 (GPIO5 ← divisor do YF-S201)
jmp([hx("I8"), (X(8), ch["I8E6"]), (X(6), ch["I8E6"]), hx("E6")], "#7b1fa2", "I8", "E6")
# I4 -> B23 (GPIO2 -> JSN RX)
jmp([hx("I4"), (X(4), ch["I4B23"]), (X(23), ch["I4B23"]), hx("B23")], "#2e7d32", "I4", "B23")
# I5 -> E13 (GPIO4 ← divisor do eco)
jmp([hx("I5"), (X(5), ch["I5E13"]), (X(13), ch["I5E13"]), hx("E13")], "#00838f", "I5", "E13")
# I14 -> F26 (GPIO22 SCL)
jmp([hx("I14"), (X(14), ch["I14F26"]), (X(26), ch["I14F26"]), hx("F26")], "#f9a825", "I14", "F26")
# I15 -> F25 (GPIO23 SDA)
jmp([hx("I15"), (X(15), ch["I15F25"]), (X(25), ch["I15F25"]), hx("F25")], "#1e88e5", "I15", "F25")
# F28 -> trilho − (GND OLED)
jmp([hx("F28"), (X(30) + 13, ROW["F"]), (X(30) + 13, NEG_Y), (X(29), NEG_Y)], C_GND, "F28", "NEG")
# B25 -> trilho − (GND JSN)
jmp([hx("B25"), (X(25) + 13, ROW["B"]), (X(25) + 13, NEG_Y), (X(26), NEG_Y)], C_GND, "B25", "NEG")
# B22 -> trilho + (5V JSN)
jmp([hx("B22"), (X(21) + 13, ROW["B"]), (X(21) + 13, POS_Y), (X(21), POS_Y)], C_5V, "B22", "POS")
# VIN -> trilho +
jmp([vin, (22, vin[1]), (22, POS_Y), (X(1), POS_Y)], C_5V, "VIN", "POS")

# 2,2 kΩ  E6 -> G1 (pull-up do sinal do YF-S201 ao 3V3), por cima dos fios
e6, g1 = hx("E6"), hx("G1")
line([e6, g1], "#8a8a8a", 2.2, halo=True)
ang = math.degrees(math.atan2(g1[1] - e6[1], g1[0] - e6[0])) + 180
resistor_body((e6[0] + g1[0]) / 2, (e6[1] + g1[1]) / 2, ang, "2k2", "")
dot(*e6, "#7b1fa2", 4.2); dot(*g1, "#ef7d00", 3.5)
text((e6[0] + g1[0]) / 2 + 20, (e6[1] + g1[1]) / 2 - 12, "2,2 kΩ", 10, anchor="start", weight="bold", halo=True)

# rótulos curtos nos jumpers
text(X(1) - 2, 300, "", 8)


# --------------------------------------------------------------------------- YF-S201
yx0, yx1, yy0, yy1 = 120, 340, 735, 815
add(f'<rect x="{yx0}" y="{yy0}" width="{yx1 - yx0}" height="{yy1 - yy0}" rx="10" fill="#1d4f91" stroke="#0e2a50" stroke-width="2"/>')
add(f'<rect x="{yx0 - 22}" y="{yy0 + 22}" width="30" height="36" rx="4" fill="#163c70"/>')
add(f'<rect x="{yx1 - 8}" y="{yy0 + 22}" width="30" height="36" rx="4" fill="#163c70"/>')
text((yx0 + yx1) / 2, yy0 + 34, "Sensor de vazão", 12, weight="bold", fill="#fff")
text((yx0 + yx1) / 2, yy0 + 52, "YF-S201", 14, weight="bold", fill="#fff")
text((yx0 + yx1) / 2, yy0 + 70, "(entrada/saída de água nas laterais)", 9, fill="#bcd3f2")
lead_red, lead_blk, lead_yel = (X(3), yy0), (200, yy0), (170, yy0)
# vermelho -> trilho +
line([lead_red, (X(3), POS_Y)], "#d62828", 3.2); dot(*lead_red, "#d62828", 3.5); dot(X(3), POS_Y, "#d62828")
# preto -> trilho − (cruza o trilho + entre furos)
line([lead_blk, (lead_blk[0], 690), (X(4) + 13, 690), (X(4) + 13, NEG_Y), (X(4), NEG_Y)], "#111", 3.2); dot(*lead_blk, "#111", 3.5); dot(X(4), NEG_Y, "#111")
# amarelo -> E2 (pela margem esquerda)
line([lead_yel, (lead_yel[0], 700), (34, 700), (34, 456), (X(2), 456), hx("E2")], "#e0a800", 3.2)
dot(*lead_yel, "#e0a800", 3.5); dot(*hx("E2"), "#e0a800")
text(lead_red[0], yy0 + 14, "verm.", 8, fill="#fff"); text(lead_yel[0], yy0 + 14, "amar.", 8, fill="#fff"); text(lead_blk[0], yy0 + 14, "preto", 8, fill="#fff")

# --------------------------------------------------------------------------- anotações elétricas
def note(x, y, lines_, color="#444", anchor="start", size=10):
    for i, s in enumerate(lines_):
        text(x, y + i * 13, s, size, anchor=anchor, fill=color, halo=True)

note(86, ROW["B"] - 2, ["YF-S201: 1 kΩ em série +", "pull-up 2,2 kΩ ao 3V3 → GPIO5"], "#7b1fa2")
note(X(14) + 4, ROW["C"] + 12, ["divisor eco JSN:", "→ GPIO4 (≈ 3,4 V)"], "#00838f")
note(X(16), ROW["F"] - 4 + 0, [], "#444")

# aviso de divergência
add(f'<rect x="370" y="735" width="570" height="118" rx="8" fill="#ecf8ee" stroke="#2e7d32" stroke-width="1.8"/>')
text(386, 757, "✓ Montagem conferida com o firmware (src/main.cpp)", 13, anchor="start", weight="bold", fill="#1b5e20")
for i, s in enumerate([
    "• YF-S201 → 1 kΩ → GPIO5 (FLUXO_PIN 5, I8 → E6) · pull-up 2,2 kΩ ao 3V3 (E6–G1).",
    "• JSN-SR04M-2: trigger GPIO2 (I4 → B23) · eco → divisor → GPIO4 (I5 → E13).",
    "• OLED I2C: SDA GPIO23 (I15 → F25) · SCL GPIO22 (I14 → F26) · VDD 3V3.",
    "• LEDs via 1 kΩ: GPIO18, GPIO19 e GPIO21.",
]):
    text(386, 777 + i * 17, s, 11, anchor="start", fill="#1b3d1f")

# --------------------------------------------------------------------------- legenda
ly = 880
text(60, ly, "Legenda de cores dos fios", 12, anchor="start", weight="bold")
items = [("#ef7d00", "3V3"), ("#d62828", "5 V (VIN / trilho +)"), ("#111111", "GND (trilho −)"), ("#7b1fa2", "GPIO5 (sinal YF-S201)"),
         ("#2e7d32", "GPIO2 (trigger JSN)"), ("#00838f", "GPIO4 (eco JSN)"), ("#f9a825", "GPIO22 (SCL)"), ("#1e88e5", "GPIO23 (SDA)"),
         ("#e0a800", "fio amarelo do YF-S201")]
for i, (col, nm) in enumerate(items):
    x = 60 + (i % 5) * 180; y = ly + 22 + (i // 5) * 22
    add(f'<rect x="{x}" y="{y - 9}" width="26" height="6" rx="3" fill="{col}" stroke="#222" stroke-width=".6"/>')
    text(x + 34, y - 2, nm, 11, anchor="start")
text(60, ly + 76, "Resistores: 5 × 1 kΩ (D2–D6, C9–H9, C10–H10, C11–H11, D13–D24) e 2 × 2,2 kΩ (E6–G1, pull-up ao 3V3; C13 ao trilho −). "
     "LEDs: catodo no trilho −, anodo em A9, A10 e A11.", 10, anchor="start", fill="#555")
text(60, ly + 92, "Alimentação: VIN do ESP32 (5 V do USB) → trilho +. O OLED usa 3V3 (I1 → F27).", 10, anchor="start", fill="#555")

add('</svg>')
open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "diagrama-protoboard.svg"), "w", encoding="utf-8").write("\n".join(out))
print("ok: diagrama-protoboard.svg")
