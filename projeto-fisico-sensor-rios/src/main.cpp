#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================
// PINOS DO PROJETO
// ============================================================

// ---------------- OLED ----------------
#define OLED_SDA 23
#define OLED_SCL 22
#define OLED_ADDR 0x3C

// -------- JSN-SR04M-2 -----------------
#define JSN_RX 2   // D2 -> RX do sensor
#define JSN_TX 4   // D4 <- TX do sensor

// -------- YF-S201 ---------------------
#define FLUXO_PIN 5   // D5 <- sinal do YF-S201

// --------------- LEDs -----------------
#define LED_VERDE 18
#define LED_AMARELO 19
#define LED_VERMELHO 21

// ============================================================
// CONFIGURAÇÃO DO OLED
// ============================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    &Wire,
    -1
);

// ============================================================
// CALIBRAÇÃO DO SENSOR DE NÍVEL
// ============================================================

// Distância considerada como reservatório VAZIO
const float DISTANCIA_VAZIO_CM = 30.0;

// Distância considerada como reservatório CHEIO
const float DISTANCIA_CHEIO_CM = 20.0;

// ============================================================
// CONFIGURAÇÃO DO YF-S201
// ============================================================

// Aproximadamente 450 pulsos correspondem a 1 litro
const float PULSOS_POR_LITRO = 450.0;

// Calcula a vazão a cada 2 segundos
const unsigned long TEMPO_VAZAO = 2000;

// ============================================================
// VARIÁVEIS
// ============================================================

volatile unsigned long pulsos = 0;

unsigned long inicioVazao = 0;

float distancia = -1.0;
float nivelPercentual = 0.0;
float vazao = 0.0;

String statusNivel = "INICIANDO";

// ============================================================
// INTERRUPÇÃO DO YF-S201
// ============================================================

void IRAM_ATTR contarPulso()
{
    pulsos++;
}

// ============================================================
// MEDIÇÃO DO JSN-SR04M-2
// ============================================================

float medirDistancia()
{
    // Garante estado inicial LOW
    digitalWrite(JSN_RX, LOW);
    delayMicroseconds(2);

    // Trigger de 120 microssegundos
    digitalWrite(JSN_RX, HIGH);
    delayMicroseconds(120);
    digitalWrite(JSN_RX, LOW);

    // Aguarda o sinal de echo por até 40 ms
    unsigned long duracao = pulseIn(
        JSN_TX,
        HIGH,
        40000
    );

    // Nenhum echo recebido
    if (duracao == 0)
    {
        return -1.0;
    }

    // Conversão do tempo para centímetros
    float distanciaCm = duracao * 0.0343 / 2.0;

    // Descarta leituras fora da faixa esperada
    if (distanciaCm < 20.0 || distanciaCm > 600.0)
    {
        return -1.0;
    }

    return distanciaCm;
}

// ============================================================
// CONVERSÃO DA DISTÂNCIA PARA PORCENTAGEM
// ============================================================

float calcularNivel(float distanciaCm)
{
    // Mantém o valor anterior se a leitura for inválida
    if (distanciaCm < 0)
    {
        return nivelPercentual;
    }

    // Reservatório vazio
    if (distanciaCm >= DISTANCIA_VAZIO_CM)
    {
        return 0.0;
    }

    // Reservatório cheio
    if (distanciaCm <= DISTANCIA_CHEIO_CM)
    {
        return 100.0;
    }

    // Conversão linear
    float nivel =
        (
            (DISTANCIA_VAZIO_CM - distanciaCm)
            /
            (DISTANCIA_VAZIO_CM - DISTANCIA_CHEIO_CM)
        ) * 100.0;

    // Garante limite de 0 a 100%
    if (nivel < 0.0)
    {
        nivel = 0.0;
    }

    if (nivel > 100.0)
    {
        nivel = 100.0;
    }

    return nivel;
}

// ============================================================
// ATUALIZA LEDs E STATUS
// ============================================================

void atualizarStatus()
{
    // -----------------------------
    // MENOS DE 33%
    // -----------------------------
    if (nivelPercentual < 33.0)
    {
        digitalWrite(LED_VERDE, HIGH);
        digitalWrite(LED_AMARELO, LOW);
        digitalWrite(LED_VERMELHO, LOW);

        statusNivel = "NORMAL";
    }

    // -----------------------------
    // 33% ATÉ 66%
    // -----------------------------
    else if (nivelPercentual <= 66.0)
    {
        digitalWrite(LED_VERDE, LOW);
        digitalWrite(LED_AMARELO, HIGH);
        digitalWrite(LED_VERMELHO, LOW);

        statusNivel = "ATENCAO";
    }

    // -----------------------------
    // ACIMA DE 66%
    // -----------------------------
    else
    {
        digitalWrite(LED_VERDE, LOW);
        digitalWrite(LED_AMARELO, LOW);
        digitalWrite(LED_VERMELHO, HIGH);

        statusNivel = "PERIGO";
    }
}

// ============================================================
// CÁLCULO DA VAZÃO
// ============================================================

void calcularVazao()
{
    unsigned long agora = millis();

    // Faz um novo cálculo a cada 2 segundos
    if (agora - inicioVazao >= TEMPO_VAZAO)
    {
        // Copia e zera o contador de pulsos
        noInterrupts();

        unsigned long quantidadePulsos = pulsos;

        pulsos = 0;

        interrupts();

        // ----------------------------------------------------
        // CÁLCULO
        // ----------------------------------------------------
        //
        // 450 pulsos = aproximadamente 1 litro
        //
        // Estamos medindo durante 2 segundos.
        //
        // Existem 60 segundos em 1 minuto:
        //
        // 60 / 2 = 30
        //
        // Portanto:
        //
        // Vazão = pulsos / 450 * 30
        //

        vazao =
            (quantidadePulsos / PULSOS_POR_LITRO) * 30.0;

        inicioVazao = agora;

        // ----------------------------------------------------
        // MONITOR SERIAL
        // ----------------------------------------------------

        Serial.println("==============================");

        Serial.print("Pulsos em 2 segundos: ");
        Serial.println(quantidadePulsos);

        Serial.print("Vazao: ");
        Serial.print(vazao, 2);
        Serial.println(" L/min");

        Serial.println("==============================");
    }
}

// ============================================================
// ATUALIZA OLED
// ============================================================

void atualizarDisplay()
{
    display.clearDisplay();

    display.setTextColor(SSD1306_WHITE);

    // -----------------------------
    // NÍVEL
    // -----------------------------

    display.setTextSize(1);
    display.setCursor(0, 0);

    display.print("Nivel:");

    display.setTextSize(2);
    display.setCursor(45, 0);

    display.print(nivelPercentual, 0);
    display.print("%");

    // -----------------------------
    // DISTÂNCIA
    // -----------------------------

    display.setTextSize(1);
    display.setCursor(0, 22);

    if (distancia < 0)
    {
        display.print("Dist: ERRO");
    }
    else
    {
        display.print("Dist: ");
        display.print(distancia, 1);
        display.print(" cm");
    }

    // -----------------------------
    // VAZÃO
    // -----------------------------

    display.setCursor(0, 34);

    display.print("Vazao: ");
    display.print(vazao, 2);
    display.print(" L/min");

    // -----------------------------
    // STATUS
    // -----------------------------

    display.setCursor(0, 50);

    display.print("Status: ");
    display.print(statusNivel);

    display.display();
}

// ============================================================
// SETUP
// ============================================================

void setup()
{
    // -----------------------------
    // SERIAL
    // -----------------------------

    Serial.begin(115200);

    // -----------------------------
    // JSN-SR04M-2
    // -----------------------------

    pinMode(JSN_RX, OUTPUT);
    pinMode(JSN_TX, INPUT);

    digitalWrite(JSN_RX, LOW);

    // -----------------------------
    // YF-S201
    // -----------------------------

    // Pull-up interno da ESP32
    pinMode(FLUXO_PIN, INPUT_PULLUP);

    // -----------------------------
    // LEDs
    // -----------------------------

    pinMode(LED_VERDE, OUTPUT);
    pinMode(LED_AMARELO, OUTPUT);
    pinMode(LED_VERMELHO, OUTPUT);

    digitalWrite(LED_VERDE, LOW);
    digitalWrite(LED_AMARELO, LOW);
    digitalWrite(LED_VERMELHO, LOW);

    // -----------------------------
    // INTERRUPÇÃO DO YF-S201
    // -----------------------------

    attachInterrupt(
        digitalPinToInterrupt(FLUXO_PIN),
        contarPulso,
        RISING
    );

    // -----------------------------
    // I2C DO OLED
    // -----------------------------

    Wire.begin(
        OLED_SDA,
        OLED_SCL
    );

    // -----------------------------
    // OLED
    // -----------------------------

    if (!display.begin(
            SSD1306_SWITCHCAPVCC,
            OLED_ADDR
        ))
    {
        Serial.println("ERRO: OLED nao encontrado!");

        while (true)
        {
            delay(1000);
        }
    }

    // -----------------------------
    // TELA INICIAL
    // -----------------------------

    display.clearDisplay();

    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);

    display.setCursor(0, 0);
    display.println("MONITORAMENTO");

    display.setCursor(0, 15);
    display.println("DO RIO");

    display.setCursor(0, 35);
    display.println("Inicializando...");

    display.display();

    // -----------------------------
    // INICIA CONTAGEM DA VAZÃO
    // -----------------------------

    inicioVazao = millis();

    delay(1500);

    Serial.println();
    Serial.println("==============================");
    Serial.println(" MONITORAMENTO DO RIO");
    Serial.println("==============================");
    Serial.println();

    Serial.println("YF-S201 configurado no GPIO 5");
    Serial.println("Janela de vazao: 2 segundos");
    Serial.println();
}

// ============================================================
// LOOP PRINCIPAL
// ============================================================

void loop()
{
    // ========================================================
    // SENSOR ULTRASSÔNICO
    // ========================================================

    float novaDistancia = medirDistancia();

    if (novaDistancia >= 0)
    {
        // Atualiza somente quando a leitura é válida
        distancia = novaDistancia;

        nivelPercentual =
            calcularNivel(distancia);

        Serial.print("Distancia: ");
        Serial.print(distancia, 1);
        Serial.println(" cm");

        Serial.print("Nivel: ");
        Serial.print(nivelPercentual, 1);
        Serial.println("%");
    }
    else
    {
        // Mantém a última leitura válida
        Serial.println(
            "Erro na leitura do JSN-SR04M-2 - mantendo ultima leitura"
        );
    }

    // ========================================================
    // LEDs
    // ========================================================

    atualizarStatus();

    // ========================================================
    // VAZÃO
    // ========================================================

    calcularVazao();

    // ========================================================
    // OLED
    // ========================================================

    atualizarDisplay();

    // Intervalo entre leituras
    delay(200);
}