# Lista de materiais — Sensor de rios (ESP32)

Atualizada em 09/10/2026.

## Componentes

| # | Componente | Qtd. | Função no projeto |
|--:|---|:--:|---|
| 1 | ESP32 DEVKIT V1 | 1 | Microcontrolador: lê os sensores, calcula nível e vazão, controla LEDs e display |
| 2 | Protoboard de 400 pontos | 1 | Montagem do circuito sem solda |
| 3 | Sensor de vazão YF-S201 | 1 | Gera pulsos proporcionais ao fluxo de água (≈ 450 pulsos/litro) |
| 4 | Sensor ultrassônico JSN-SR04M-2 | 1 | Mede a distância até a superfície da água (nível do rio) |
| 5 | Display OLED SSD1306 de 0,96" I2C | 1 | Exibe nível, distância, vazão e status |
| 6 | LED vermelho | 1 | Status PERIGO |
| 7 | LED amarelo | 1 | Status ATENÇÃO |
| 8 | LED verde | 1 | Status NORMAL |
| 9 | Resistor de 1 kΩ | 5 | 3 em série com os LEDs e 2 como parte de cima dos divisores de tensão |
| 10 | Resistor de 2,2 kΩ | 2 | Parte de baixo (para o terra) dos divisores de tensão |
| 11 | Jumpers | 11 | Ligações entre ESP32, display, sensores e trilhos (lista completa abaixo) |

## Uso dos resistores

| Resistor | Entre | Função |
|---|---|---|
| 1 kΩ | D2 e D6 | Série no sinal do YF-S201 (divisor) |
| 2,2 kΩ | C6 e trilho − | Terra do divisor do YF-S201 |
| 1 kΩ | D13 e D24 | Série no eco do JSN-SR04M-2 (divisor) |
| 2,2 kΩ | C13 e trilho − | Terra do divisor do eco |
| 1 kΩ | C9 e H9 | LED 1 (GPIO18) |
| 1 kΩ | C10 e H10 | LED 2 (GPIO19) |
| 1 kΩ | C11 e H11 | LED 3 (GPIO21) |

Os divisores reduzem os 5 V do YF-S201 e do eco do JSN-SR04M-2 para ≈ 3,44 V
(`5 V × 2,2 / (1 + 2,2)`), compatível com as entradas do ESP32.

## Jumpers (11)

I1 → F27 · I2 → trilho − · I8 → E6 · I4 → B23 · I5 → E13 · I14 → F26 · I15 → F25 · F28 → trilho − · B25 → trilho − ·
B22 → trilho + · VIN → trilho +.

Função de cada um e diagrama completo:
[`../projeto-fisico-sensor-rios/diagrama/conexoes-protoboard.md`](../projeto-fisico-sensor-rios/diagrama/conexoes-protoboard.md).

## Ligações de pinos (firmware físico)

Conforme `projeto-fisico-sensor-rios/src/main.cpp`.

| Dispositivo | Sinal | GPIO do ESP32 |
|---|---|:--:|
| OLED SSD1306 (I2C, endereço 0x3C) | SDA | 23 |
| OLED SSD1306 (I2C, endereço 0x3C) | SCL | 22 |
| JSN-SR04M-2 | Trigger (`JSN_RX`) | 2 |
| JSN-SR04M-2 | Eco (`JSN_TX`), via divisor | 4 |
| YF-S201 | Pulsos (`FLUXO_PIN`), via divisor | 5 |
| LED verde | Anodo, via 1 kΩ | 18 |
| LED amarelo | Anodo, via 1 kΩ | 19 |
| LED vermelho | Anodo, via 1 kΩ | 21 |

Todos os pinos conferem com a montagem na protoboard.

## Alimentação

* O ESP32 recebe 5 V pelo cabo USB. O pino VIN distribui esses 5 V no trilho positivo, que alimenta o YF-S201 e o JSN-SR04M-2.
* O display OLED é alimentado com 3,3 V, direto do pino 3V3 do ESP32.
* O cabo USB, a tubulação e a fixação mecânica dos sensores não fazem parte desta lista.
