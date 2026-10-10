# Monitoramento de Fluxo de Água com ESP32 — Sensor de rios

![Compilação](https://github.com/CaiqueRV/Monitoramento-Fluxo-de-Agua-ESP32/actions/workflows/build.yml/badge.svg)

Protótipo de monitoramento hidrológico com **ESP32** para o projeto AquaScan (rios de Petrópolis). O sensor mede o
**nível do rio** (ultrassônico JSN-SR04M-2) e a **vazão** (YF-S201), mostra os dados em um **display OLED SSD1306** e
sinaliza o estado com **LEDs** (verde = normal, amarelo = atenção, vermelho = perigo).

![Diagrama das conexões na protoboard](projeto-fisico-sensor-rios/diagrama/diagrama-protoboard.png)

## Estrutura do repositório

| Pasta / arquivo | Conteúdo |
|---|---|
| [`projeto-fisico-sensor-rios/`](projeto-fisico-sensor-rios/) | Firmware do sensor físico (PlatformIO) e [diagrama da protoboard](projeto-fisico-sensor-rios/diagrama/conexoes-protoboard.md) |
| [`simulacao-wokwi/`](simulacao-wokwi/) | Simulação no Wokwi: `sketch.ino`, `diagram.json`, `libraries.txt` |
| [`modelo-calibracao/`](modelo-calibracao/) | Análise dos cálculos de nível e vazão e script Python que os reproduz |
| [`hardware/`](hardware/lista-de-materiais.md) | Lista de materiais e ligações de pinos |
| [`dados/calibracao/`](dados/calibracao/modelo-calibracao.csv) | Planilha para registrar os ensaios de calibração |
| [`docs/`](docs/) | Documentação do protótipo anterior (v0.1.0, somente vazão) |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de mudanças |
| `.github/workflows/build.yml` | Compilação automática do firmware físico |

## Como cada medida é calculada

| Medida | Sensor | Cálculo (firmware físico) |
|---|---|---|
| Distância | JSN-SR04M-2 | `duração do eco (µs) × 0,0343 / 2` (cm) |
| Nível | JSN-SR04M-2 | `(30 − distância) / (30 − 20) × 100` (%), limitado a 0–100 |
| Vazão | YF-S201 | `(pulsos em 2 s / 450) × 30` (L/min) |
| Status | — | < 33 % NORMAL · 33–66 % ATENÇÃO · > 66 % PERIGO |

Detalhes, tabelas, pontos de atenção e procedimento de calibração:
[`modelo-calibracao/analise-calculos-sensores.md`](modelo-calibracao/analise-calculos-sensores.md).

## Projeto físico

* Placa: ESP32 DevKit V1 (`esp32dev`), framework Arduino, monitor serial a 115200 baud.
* Bibliotecas: Adafruit GFX Library e Adafruit SSD1306 (instaladas pelo PlatformIO).

```bash
cd projeto-fisico-sensor-rios
pio run                # compilar
pio run -t upload      # gravar no ESP32
pio device monitor     # monitor serial
```

| Função | GPIO no firmware |
|---|:--:|
| OLED SDA / SCL | 23 / 22 |
| JSN-SR04M-2 trigger / eco | 2 / 4 |
| YF-S201 (pulsos) | 5 |
| LED verde / amarelo / vermelho | 18 / 19 / 21 |

Os pinos conferem com a montagem na protoboard; a verificação é feita por
[`verificar_conexoes.py`](projeto-fisico-sensor-rios/diagrama/verificar_conexoes.py).

## Simulação Wokwi

Projeto online: <https://wokwi.com/projects/476706772789091329>

Na simulação, o HC-SR04 representa o JSN-SR04M-2 e um botão representa os pulsos do YF-S201. Os parâmetros diferem
do físico (referência de 100 cm para o nível e janela de 10 s para a vazão); a comparação está na
[seção 7 da análise de cálculos](modelo-calibracao/analise-calculos-sensores.md#7-diferenças-em-relação-à-simulação-wokwi).

Ligações da simulação e equivalência com o hardware real: [`simulacao-wokwi/README.md`](simulacao-wokwi/README.md).

## Materiais

ESP32 DEVKIT V1, protoboard de 400 pontos, sensor de vazão YF-S201, sensor ultrassônico JSN-SR04M-2, display OLED
SSD1306 de 0,96" I2C, LED vermelho, LED amarelo, LED verde, 5 resistores de 1 kΩ, 2 resistores de 2,2 kΩ e 11 jumpers.
Lista completa: [`hardware/lista-de-materiais.md`](hardware/lista-de-materiais.md).

## Documentação do protótipo anterior (v0.1.0)

A pasta [`docs/`](docs/) descreve o primeiro protótipo, que media apenas a vazão (YF-S201 + OLED + um LED, simulado com
potenciômetro no GPIO27). Esses documentos ainda **não foram atualizados** para o sensor de rios e podem citar pinos e
arquivos que não existem mais na raiz:

* [`docs/readme-v0.1.0-fluxo.md`](docs/readme-v0.1.0-fluxo.md): README anterior, arquivado
* [`docs/documentacao-completa.md`](docs/documentacao-completa.md), [`docs/decisoes.md`](docs/decisoes.md),
  [`docs/calibracao.md`](docs/calibracao.md), [`docs/validacao.md`](docs/validacao.md)

## Limitações atuais

* O nível usa uma faixa de apenas 10 cm (1 cm = 10 %), o que limita a resolução; veja os pontos de atenção na análise de cálculos.
* O sistema ainda não prevê transbordamento nem envia dados pela rede.
* A protoboard é só para protótipo: uma instalação real exige solda, caixa vedada e proteção contra umidade.
