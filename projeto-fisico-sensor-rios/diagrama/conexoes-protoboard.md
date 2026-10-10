# Conexões na protoboard de 400 pontos

![Diagrama das conexões na protoboard](diagrama-protoboard.png)

Arquivos: [`diagrama-protoboard.svg`](diagrama-protoboard.svg) (vetorial) ·
[`gerar_diagrama.py`](gerar_diagrama.py) (gera o SVG) · [`verificar_conexoes.py`](verificar_conexoes.py) (confere os nós elétricos).

## Como ler as coordenadas

* Colunas numeradas de 1 a 30 e linhas de A a J.
* Em cada coluna, os furos **A–E** são ligados entre si, e os furos **F–J** também. O canal central **separa** as duas metades.
* Os trilhos **negativo (−)** e **positivo (+)** são ligados ao longo de todo o comprimento.
* O ESP32 está plugado na linha **J** (colunas 1 a 15); o OLED, na linha **G** (colunas 25 a 28); o módulo JSN-SR04M-2, na linha **A** (colunas 22 a 25).

## Posição dos componentes

| Componente | Pino | Furo |
|---|---|---|
| ESP32 | 3V3, GND, D15, D2, D4, RX2, TX2, D5 | J1, J2, J3, J4, J5, J6, J7, J8 |
| ESP32 | D18, D19, D21, RX0, TX0, D22, D23 | J9, J10, J11, J12, J13, J14, J15 |
| OLED SSD1306 | GND, VDD, SCK (SCL), SDA | G28, G27, G26, G25 |
| JSN-SR04M-2 | GND, TX (eco), RX (trigger), 5V | A25, A24, A23, A22 |
| YF-S201 | vermelho / preto / amarelo | trilho + / trilho − / E2 |
| LED 1, 2, 3 | anodo (catodo no trilho −) | A9, A10, A11 |

## Jumpers (11)

| Jumper | Liga | Função |
|---|---|---|
| I1 → F27 | 3V3 → OLED VDD | Alimenta o display com 3,3 V |
| I2 → trilho − | GND do ESP32 → trilho − | Referência de terra |
| I8 → E6 | GPIO5 → nó do sinal do YF-S201 (coluna 6) | Entrada do sinal de vazão |
| I4 → B23 | GPIO2 → RX do JSN-SR04M-2 | Trigger do ultrassônico |
| I5 → E13 | GPIO4 → ponto central do divisor do eco | Leitura do eco do ultrassônico |
| I14 → F26 | GPIO22 → SCK do OLED | I2C SCL |
| I15 → F25 | GPIO23 → SDA do OLED | I2C SDA |
| F28 → trilho − | GND do OLED → trilho − | Terra do display |
| B25 → trilho − | GND do JSN-SR04M-2 → trilho − | Terra do ultrassônico |
| B22 → trilho + | 5V do JSN-SR04M-2 → trilho + | Alimentação do ultrassônico |
| VIN → trilho + | VIN do ESP32 → trilho + | Distribui os 5 V do USB |

## Resistores (5 × 1 kΩ e 2 × 2,2 kΩ)

| Resistor | Entre | Função |
|---|---|---|
| 1 kΩ | D2 e D6 | Em série no sinal do YF-S201 |
| 2,2 kΩ | E6 e G1 | Pull-up do sinal do YF-S201 ao 3V3 (G1 está na coluna 1, a mesma do pino 3V3) |
| 1 kΩ | D13 e D24 | Em série no eco (TX) do JSN-SR04M-2 (parte de cima do divisor) |
| 2,2 kΩ | C13 e trilho − | Parte de baixo do divisor do eco |
| 1 kΩ | C9 e H9 | LED 1 → GPIO18 |
| 1 kΩ | C10 e H10 | LED 2 → GPIO19 |
| 1 kΩ | C11 e H11 | LED 3 → GPIO21 |

**Sinal do YF-S201: pull-up ao 3V3.** O fio amarelo (E2) passa pelo 1 kΩ (D2–D6) até a coluna 6, onde estão o GPIO5
(jumper `I8 → E6`) e o 2,2 kΩ que sobe até o 3V3 (`E6 → G1`). É a ligação indicada quando a saída do sensor é em
**coletor aberto**, isto é, o sensor só puxa a linha para o GND e o nível alto vem do pull-up. Com o 2,2 kΩ para o terra,
como estava antes, uma saída desse tipo deixaria a linha sempre em nível baixo.

Níveis esperados no GPIO5 com saída em coletor aberto:

| Saída do YF-S201 | Tensão no GPIO5 | Leitura |
|---|---|---|
| Aberta (não conduz) | 3,3 V, pelo pull-up | Alto |
| Conduzindo para o GND | `3,3 V × 1 / (1 + 2,2)` ≈ 1,03 V | Baixo, sem margem* |

\* O ESP32 só garante leitura de nível baixo abaixo de `0,25 × 3,3 V` ≈ 0,83 V. Com 1,03 V o pino está na faixa
indefinida: na prática costuma ser lido como baixo, mas fica sensível a ruído e pode perder pulsos. Trocar o 1 kΩ
(D2–D6) por um jumper leva o nível baixo para perto de 0 V.

Se a saída do seu YF-S201 fornecer 5 V ativamente (em vez de coletor aberto), o nível alto subiria para ≈ 4,5 V
(`(5/1 + 3,3/2,2) / (1/1 + 1/2,2)`), acima dos 3,6 V máximos da entrada do ESP32; nesse caso o divisor para o terra
seria o correto. Para confirmar, meça a tensão no D5 com um multímetro girando o rotor devagar: ela deve alternar
entre cerca de 3,3 V e um valor baixo, sem nunca passar de 3,3 V.

**Eco do JSN-SR04M-2: divisor de tensão.** O eco (A24 → D24) sai em 5 V, passa por 1 kΩ em série (D13–D24) e por
2,2 kΩ para o terra (C13), e o ESP32 lê no ponto central:

```
Vsaída = 5 V × 2,2 kΩ / (1 kΩ + 2,2 kΩ) ≈ 3,44 V
```

Esse valor fica ligeiramente acima de 3,3 V, mas abaixo do máximo de 3,6 V das entradas do ESP32. Com 1 kΩ + 2 kΩ seriam 3,33 V.

## Nós elétricos resultantes

Resultado de `python3 verificar_conexoes.py`, que aplica todas as conexões acima ao modelo da protoboard:

| Nó | Pinos ligados |
|---|---|
| GND (trilho −) | ESP32 GND, OLED GND, JSN GND, YF-S201 preto, catodos dos 3 LEDs, 2,2 kΩ do divisor do eco |
| 5 V (trilho +) | ESP32 VIN, JSN 5V, YF-S201 vermelho |
| 3,3 V (colunas 1 e 27, F–J) | ESP32 3V3, OLED VDD, 2,2 kΩ do pull-up do YF-S201 (G1) |
| I2C SCL (coluna 26, F–J) | ESP32 D22, OLED SCK |
| I2C SDA (coluna 25, F–J) | ESP32 D23, OLED SDA |
| Trigger (coluna 23, A–E) | ESP32 D2, JSN RX |
| Eco, ponto central (coluna 13, A–E) | ESP32 D4, 1 kΩ (D13) vindo do JSN TX, 2,2 kΩ para o trilho − |
| Vazão (coluna 6, A–E) | ESP32 D5, 1 kΩ (D6) vindo do YF-S201, 2,2 kΩ (E6) para o 3V3 |

Os pinos D15, RX2, TX2, RX0 e TX0 do ESP32 ficam sem ligação. D18, D19 e D21 só têm o resistor de 1 kΩ do LED correspondente.

## Conferência com o firmware

Comparação entre a montagem e `../src/main.cpp`:

| Função | GPIO no firmware | GPIO na montagem | Situação |
|---|:--:|:--:|---|
| OLED SDA | 23 | 23 (I15 → F25) | Confere |
| OLED SCL | 22 | 22 (I14 → F26) | Confere |
| JSN-SR04M-2 trigger (`JSN_RX`) | 2 | 2 (I4 → B23) | Confere |
| JSN-SR04M-2 eco (`JSN_TX`) | 4 | 4 (I5 → E13, via divisor) | Confere |
| LED verde | 18 | 18 (C9–H9) | Confere, se o LED 1 for verde |
| LED amarelo | 19 | 19 (C10–H10) | Confere, se o LED 2 for amarelo |
| LED vermelho | 21 | 21 (C11–H11) | Confere, se o LED 3 for vermelho |
| YF-S201 (`FLUXO_PIN`) | 5 | 5 (I8 → E6, via 1 kΩ, com pull-up de 2,2 kΩ ao 3V3) | Confere |

O próprio `verificar_conexoes.py` faz essa conferência: ele lê os `#define` de pinos em `../src/main.cpp` e testa cada
um contra os nós da montagem (ligação direta, ou através do resistor de 1 kΩ no caso do eco, do YF-S201 e dos LEDs; o pull-up de 2,2 kΩ do YF-S201 ao 3V3 também é conferido).
Resultado atual: **todas as ligações conferem**. Se uma conexão da protoboard ou um pino do firmware mudar, rode o script
de novo e atualize a lista de jumpers em `verificar_conexoes.py` e `gerar_diagrama.py`.

```bash
python3 verificar_conexoes.py   # sai com código 1 se houver divergência
python3 gerar_diagrama.py       # regenera diagrama-protoboard.svg
```
