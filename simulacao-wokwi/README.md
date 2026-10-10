# Simulação Wokwi

Projeto: <https://wokwi.com/projects/476706772789091329> ("Prototipo 1 sensor").

Os três arquivos desta pasta são a versão atual do projeto no Wokwi:

| Arquivo | Conteúdo |
|---|---|
| `sketch.ino` | Código da simulação |
| `diagram.json` | Circuito: ESP32 DevKitC V4, meia protoboard, HC-SR04, botão, OLED SSD1306, 3 LEDs e 3 resistores de 1 kΩ |
| `libraries.txt` | Bibliotecas: Adafruit GFX Library e Adafruit SSD1306 |

## Como usar

1. Abra o projeto no link acima, ou crie um projeto **ESP32** em [wokwi.com](https://wokwi.com).
2. Cole `sketch.ino`, `diagram.json` e `libraries.txt` nas abas de mesmo nome.
3. Inicie a simulação. Cada clique no botão amarelo equivale a um pulso do YF-S201; para mudar o nível, clique no HC-SR04 e ajuste a distância.

## Ligações da simulação

Conferidas contra os pinos do `sketch.ino` (todas coincidem).

| Componente | Pino | Ligação no ESP32 |
|---|---|---|
| LED vermelho | anodo, via 1 kΩ (r1) | GPIO 25 |
| LED amarelo | anodo, via 1 kΩ (r2) | GPIO 26 |
| LED verde | anodo, via 1 kΩ (r3) | GPIO 27 |
| LEDs | catodos | GND.1 (coluna 14 da protoboard) |
| HC-SR04 | VCC / TRIG / ECHO / GND | 5V / GPIO 32 / GPIO 34 / GND.2 |
| Botão | um lado / outro lado | GPIO 33 (`INPUT_PULLUP`, borda `FALLING`) / GND.3 |
| OLED SSD1306 (0x3C) | VCC / GND / SDA / SCL | 3V3 / GND.1 / GPIO 21 / GPIO 22 |

## Equivalência com o hardware real

| Hardware real | Na simulação |
|---|---|
| ESP32 DEVKIT V1 | ESP32 DevKitC V4 (`board-esp32-devkit-c-v4`) |
| Protoboard de 400 pontos | Meia protoboard (`wokwi-breadboard-half`) |
| JSN-SR04M-2 | HC-SR04 |
| YF-S201 | Botão |
| Divisores de tensão 1 kΩ + 2,2 kΩ | Não usados: no Wokwi não há risco de 5 V nas entradas |

Os pinos da simulação são diferentes dos do projeto físico (veja [`../hardware/lista-de-materiais.md`](../hardware/lista-de-materiais.md)).

## Parâmetros da simulação

* Nível: `(100 − distância) / 100 × 100`, ou seja, 0 % a 100 cm (`ALTURA_MAXIMA_CM`).
* Vazão: janela de 10 s, `(pulsos / 10) / 7,5` L/min.
* Status: < 33 % NORMAL, < 66 % ATENCAO, demais PERIGO.

As diferenças em relação ao firmware físico estão na seção 7 de
[`../modelo-calibracao/analise-calculos-sensores.md`](../modelo-calibracao/analise-calculos-sensores.md).
