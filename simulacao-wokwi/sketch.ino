#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// =========================
// OLED
// =========================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// =========================
// PINOS
// =========================

// LEDs
#define LED_VERMELHO 25
#define LED_AMARELO  26
#define LED_VERDE    27

// HC-SR04
// Representa o JSN-SR04M
#define TRIG_PIN 32
#define ECHO_PIN 34

// Pushbutton
// Representa os pulsos do YF-S201
#define FLUXO_PIN 33

// =========================
// CONFIGURAÇÕES
// =========================

// Distância correspondente a 0%
// Neste teste estamos usando 100 cm.
#define ALTURA_MAXIMA_CM 100.0

// YF-S201
// Frequência aproximada:
// 7,5 pulsos/segundo para cada L/min
#define PULSOS_POR_LITRO_MIN 7.5

// Tempo usado para calcular a vazão
#define TEMPO_MEDICAO_FLUXO 10000

// =========================
// VARIÁVEIS
// =========================

volatile unsigned long pulsos = 0;

unsigned long inicioMedicaoFluxo = 0;

float vazao = 0.0;
float distancia = 0.0;
float nivelPercentual = 0.0;

// =========================
// INTERRUPÇÃO
// =========================

void contarPulso() {
  pulsos++;
}

// =========================
// MEDIR DISTÂNCIA
// =========================

float medirDistancia() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duracao = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duracao == 0) {
    return -1;
  }

  float distanciaCM = duracao * 0.0343 / 2.0;

  return distanciaCM;
}

// =========================
// CALCULAR NÍVEL
// =========================

float calcularNivel(float distanciaCM) {

  // Água abaixo do limite
  if (distanciaCM >= ALTURA_MAXIMA_CM) {
    return 0.0;
  }

  // Água no nível máximo
  if (distanciaCM <= 0) {
    return 100.0;
  }

  float nivel =
    ((ALTURA_MAXIMA_CM - distanciaCM)
    / ALTURA_MAXIMA_CM) * 100.0;

  return nivel;
}

// =========================
// ATUALIZAR LEDs
// =========================

void atualizarLEDs(float nivel) {

  // Primeiro desliga todos
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_AMARELO, LOW);
  digitalWrite(LED_VERMELHO, LOW);

  if (nivel < 33.0) {

    digitalWrite(LED_VERDE, HIGH);

  } else if (nivel < 66.0) {

    digitalWrite(LED_AMARELO, HIGH);

  } else {

    digitalWrite(LED_VERMELHO, HIGH);
  }
}

// =========================
// ESTADO DO RIO
// =========================

String obterEstado(float nivel) {

  if (nivel < 33.0) {
    return "NORMAL";
  }

  if (nivel < 66.0) {
    return "ATENCAO";
  }

  return "PERIGO";
}

// =========================
// CALCULAR VAZÃO
// =========================

void calcularVazao() {

  unsigned long agora = millis();

  // Só calcula depois de 10 segundos
  if (agora - inicioMedicaoFluxo >= TEMPO_MEDICAO_FLUXO) {

    // Guarda a quantidade de pulsos
    noInterrupts();

    unsigned long pulsosMedidos = pulsos;

    pulsos = 0;

    interrupts();

    // Frequência em pulsos por segundo
    float frequencia = pulsosMedidos / 10.0;

    // Q = F / 7,5
    vazao = frequencia / PULSOS_POR_LITRO_MIN;

    // Reinicia a janela de medição
    inicioMedicaoFluxo = agora;

    // Mostra no Serial
    Serial.println("----------------------------");
    Serial.print("Pulsos em 10 segundos: ");
    Serial.println(pulsosMedidos);

    Serial.print("Frequencia: ");
    Serial.print(frequencia);
    Serial.println(" Hz");

    Serial.print("Vazao: ");
    Serial.print(vazao, 2);
    Serial.println(" L/min");
  }
}

// =========================
// ATUALIZAR DISPLAY
// =========================

void atualizarDisplay() {

  String estado = obterEstado(nivelPercentual);

  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);

  // Título
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("MONITORAMENTO DO RIO");

  display.drawLine(0, 10, 127, 10, SSD1306_WHITE);

  // Nível
  display.setCursor(0, 16);
  display.print("Nivel: ");

  display.setTextSize(2);
  display.print(nivelPercentual, 1);
  display.println("%");

  // Vazão
  display.setTextSize(1);
  display.setCursor(0, 38);
  display.print("Vazao: ");
  display.print(vazao, 2);
  display.println(" L/min");

  // Estado
  display.setCursor(0, 53);
  display.print("Estado: ");
  display.print(estado);

  display.display();
}

// =========================
// SETUP
// =========================

void setup() {

  Serial.begin(115200);

  // LEDs
  pinMode(LED_VERMELHO, OUTPUT);
  pinMode(LED_AMARELO, OUTPUT);
  pinMode(LED_VERDE, OUTPUT);

  // HC-SR04
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // YF-S201 / botão
  pinMode(FLUXO_PIN, INPUT_PULLUP);

  // Interrupção
  attachInterrupt(
    digitalPinToInterrupt(FLUXO_PIN),
    contarPulso,
    FALLING
  );

  // OLED
  Wire.begin(21, 22);

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {

    Serial.println("Erro ao iniciar OLED!");

    while (true) {
      delay(1000);
    }
  }

  // Tela inicial
  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  display.setCursor(20, 25);
  display.println("Iniciando...");

  display.display();

  delay(1500);

  // Começa a primeira janela de 10 segundos
  inicioMedicaoFluxo = millis();
}

// =========================
// LOOP
// =========================

void loop() {

  // =========================
  // NÍVEL
  // =========================

  distancia = medirDistancia();

  if (distancia >= 0) {

    nivelPercentual = calcularNivel(distancia);

    atualizarLEDs(nivelPercentual);
  }

  // =========================
  // VAZÃO
  // =========================

  calcularVazao();

  // =========================
  // DISPLAY
  // =========================

  atualizarDisplay();

  // =========================
  // SERIAL
  // =========================

  Serial.print("Distancia: ");
  Serial.print(distancia);
  Serial.print(" cm | Nivel: ");
  Serial.print(nivelPercentual);
  Serial.print("% | Vazao: ");
  Serial.print(vazao, 2);
  Serial.println(" L/min");

  delay(200);
}
