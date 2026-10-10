# Changelog

Registro das mudanças do projeto. Cada versão corresponde a uma etapa concluída do [roadmap](docs/readme-v0.1.0-fluxo.md#roadmap).

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Mudanças ainda não incluídas em uma versão ficam na seção **Não lançado**.

## [Não lançado]

Branch: `feature/sensor-rios-fisico-e-simulacao`

### Sensor de rios: projeto físico, simulação Wokwi, calibração e hardware

#### Adicionado
- `projeto-fisico-sensor-rios/`: firmware do sensor de rios físico (PlatformIO, ESP32 DevKit V1) na versão enviada em `Sensor_de_rios.zip`, com README próprio.
  - `src/main.cpp`: nível com JSN-SR04M-2 (trigger no GPIO 2, eco no GPIO 4; pulso de 120 µs, timeout de 40 ms, faixa válida de 20 a 600 cm); nível em % entre 30 cm (0 %) e 20 cm (100 %).
  - Vazão com YF-S201 no GPIO 5 por interrupção `RISING` (`IRAM_ATTR`), 450 pulsos/L e janela de 2 s.
  - LEDs: verde (GPIO 18) < 33 %, amarelo (GPIO 19) de 33 a 66 %, vermelho (GPIO 21) > 66 %.
  - OLED SSD1306 128×64 em I2C (SDA = 23, SCL = 22, endereço 0x3C) e saída no Serial a 115200 baud.
  - Em leitura inválida do ultrassônico, mantém a última distância e o último nível válidos.
  - A pasta `.pio/` (build e bibliotecas) não foi versionada.
- `projeto-fisico-sensor-rios/diagrama/`: diagrama das conexões na protoboard de 400 pontos (`diagrama-protoboard.svg` e `.png`),
  `conexoes-protoboard.md` (posição dos componentes, 11 jumpers, 7 resistores, pull-up do YF-S201 e divisor do eco com os níveis de tensão, nós elétricos e conferência com o firmware),
  `gerar_diagrama.py` (gera o SVG) e `verificar_conexoes.py` (monta os nós elétricos a partir da lista de conexões e confere cada pino definido em `src/main.cpp`, incluindo o pull-up do YF-S201; todas as ligações conferem, com o sinal do YF-S201 no GPIO 5 pelo jumper `I8 → E6`).
- `simulacao-wokwi/`: `sketch.ino`, `diagram.json` e `libraries.txt` do projeto <https://wokwi.com/projects/476706772789091329>, com README.
  - `sketch.ino`: HC-SR04 no lugar do JSN-SR04M (TRIG = 32, ECHO = 34), botão no lugar do YF-S201 (GPIO 33, borda `FALLING`), LEDs em 25/26/27, OLED em SDA 21 / SCL 22.
  - Nível em % com referência de 100 cm; vazão com janela de 10 s e `frequência / 7,5`.
  - `diagram.json`: ESP32 DevKitC V4, meia protoboard, HC-SR04 (5V), botão ligado ao GND, OLED SSD1306 (3V3) e LEDs vermelho/amarelo/verde com resistores de 1 kΩ; ligações conferidas contra os pinos do sketch.
  - `libraries.txt`: Adafruit GFX Library e Adafruit SSD1306.
- `modelo-calibracao/`: `analise-calculos-sensores.md` (como o firmware calcula distância, nível, status e vazão; procedimento de calibração; comparação físico × simulação; pontos de atenção) e `modelo_calibracao.py` (reprodução das fórmulas em Python).
- `README.md` novo, descrevendo a estrutura atual do repositório.

#### Alterado
- `hardware/lista-de-materiais.md` (estava vazio) preenchida: ESP32 DEVKIT V1, protoboard de 400 pontos, YF-S201, JSN-SR04M-2, OLED SSD1306 de 0,96" I2C, LED vermelho, LED amarelo, LED verde, 5 resistores de 1 kΩ, 2 resistores de 2,2 kΩ e 11 jumpers, com uso de cada resistor, lista de jumpers, tabela de pinos e alimentação.
- Sinal do YF-S201 na protoboard: o resistor de 2,2 kΩ passou a ligar `E6` a `G1` (pull-up ao 3V3), no lugar de `C6` ao trilho negativo. A ligação deixou de ser um divisor de tensão e virou 1 kΩ em série + pull-up de 2,2 kΩ; diagrama, verificador, conexões, lista de materiais e análise de cálculos atualizados, com os níveis de tensão esperados no GPIO 5.
- `docs/imagens/etapa-2-compilacao.png` e `docs/imagens/etapa-3-simulacao.png` substituídas pelas capturas do sensor de rios (compilação do firmware físico e simulação no Wokwi).
- `docs/validacao.md`: registradas as etapas 2 (compilação: RAM 6,9%, Flash 23,1%) e 3 (simulação: 53,44 cm → 46,56%, ATENCAO, LED amarelo, 20,95 L/min) do sensor de rios; os registros do protótipo v0.1.0 foram mantidos, sem as capturas antigas.
- `.github/workflows/build.yml`: a compilação passou a usar `pio run -d projeto-fisico-sensor-rios`, já que o `platformio.ini` deixou de ficar na raiz.
- Badge de compilação do README apontado para o repositório atual (`CaiqueRV/Monitoramento-Fluxo-de-Agua-ESP32`); o anterior apontava para outro endereço.

#### Movido / removido
- README anterior movido para `docs/readme-v0.1.0-fluxo.md`, com aviso de documento arquivado e links ajustados.
- Removidos da raiz, por serem do protótipo anterior (somente vazão, potenciômetro no GPIO 34, pulsos gerados no GPIO 26): `src/main.cpp`, `include/config.h`, `diagram.json`, `wokwi.toml` e `platformio.ini`. Continuam no histórico do Git.

#### Pendências e pontos de atenção
- As cores dos LEDs no diagrama (1 verde, 2 amarelo, 3 vermelho) foram assumidas a partir dos pinos do firmware.
- Com exceção de `docs/validacao.md`, os documentos em `docs/` ainda descrevem o protótipo v0.1.0 e não foram atualizados.
- Com o pull-up, o nível baixo no GPIO 5 fica em ≈ 1,03 V (sem margem em relação ao limite de 0,83 V do ESP32) se a saída do YF-S201 for em coletor aberto; medir a tensão no D5 para confirmar o tipo de saída. Trocar o 1 kΩ (D2–D6) por um jumper daria mais margem.
- Pontos de atenção do firmware registrados na análise de cálculos e não corrigidos: resolução de 10 % por cm, nível de 100 % só em exatamente 20,0 cm, efeito da temperatura, estado inicial NORMAL sem leitura e fronteira de 66 % diferente entre físico e simulação.
- Este changelog descreve o conteúdo das versões atuais; não foi feita comparação linha a linha com o firmware físico anterior, que não estava no repositório.

### Protótipo v0.1.0 — somente vazão (itens anteriores, em validação)

A primeira versão está em validação. Os itens abaixo foram implementados, mas só entram na **v0.1.0** depois de testados na simulação.

#### Adicionado
- Contagem de pulsos do YF-S201 por interrupção no GPIO27
- Cálculo de frequência (Hz) com correção pelo tempo real decorrido
- Cálculo de vazão (L/min) com fator de calibração 7,5
- Exibição de pulsos, frequência, vazão e alerta no OLED SSD1306
- LED de alerta quando a vazão passa de 5 L/min
- Simulação do sensor com gerador de pulsos (GPIO26) e potenciômetro (GPIO34)
- Compatibilidade com as versões 2.x e 3.x do core do ESP32
- Projeto PlatformIO com simulação pelo Wokwi para VS Code
- Configurações centralizadas em `include/config.h`
- Compilação automática com GitHub Actions
- Documentação técnica, registro de decisões, procedimento de calibração e lista de materiais
- Registro de validação por etapa em `docs/validacao.md`

#### Corrigido
- Removida a tag `v0.1.0`, criada antes de a simulação ser testada
- Quebra de linha do Monitor Serial no terminal do Wokwi (`\r\n` no lugar de `\n`)
- Fios do OLED atravessando a tela na simulação
