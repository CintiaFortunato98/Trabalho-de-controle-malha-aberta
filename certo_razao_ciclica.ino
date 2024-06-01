#include <Encoder.h>
#include <Arduino.h>

// Definições de pinos para o motor e encoder
const int CHA = 2;   // Pino A do encoder
const int CHB = 12;  // Pino B do encoder
const int IN1 = 9;   // Pino IN1 da ponte H (controle de direção)
const int IN2 = 8;   // Pino IN2 da ponte H (controle de direção)
const int ENA = 10;  // Pino ENA da ponte H (controle de velocidade)

// Constantes para configuração do encoder
const float PPR = 200.0; // Pulsos por rotação do encoder

// Razão cíclica (duty cycle) desejada
const float MIN_DUTY_CYCLE = 0.65;    // Razão cíclica mínima
const float MAX_DUTY_CYCLE = 0.85;    // Razão cíclica máxima

// Variáveis para controle de posição e velocidade
volatile long encoderCount = 0; // Contador de pulsos do encoder
volatile unsigned long lastTime = 0; // Último tempo registrado para cálculo de velocidade
double speed = 0.0; // Velocidade calculada do encoder em unidades de posição por segundo

// Variáveis para controle do PWM
float currentDutyCycle = 0.0; // Razão cíclica inicial

// Objeto Encoder
Encoder encoder(CHA, CHB);

void countPulses() {
  // Incrementa a contagem de pulsos do encoder
  if (digitalRead(CHA) == digitalRead(CHB)) {
    encoderCount++;
  } else {
    encoderCount--;
  }
}

void calculateCurrentSpeed() {
  // Calcula o tempo decorrido desde a última atualização
  unsigned long currentTime = micros();
  unsigned long timeChange = currentTime - lastTime;
  lastTime = currentTime;

  // Calcula a mudança na posição do encoder desde a última atualização
  long currentPosition = encoder.read();
  long positionChange = abs(encoderCount);
  encoderCount = 0;

  // Calcula a velocidade em unidades de posição por segundo
  if (timeChange > 0) {
    speed = (positionChange * 1000000.0) / timeChange; // Velocidade em posições por segundo
  }

  // Converte a velocidade para RPM
  float rpm = (speed / PPR) * 60.0;  // RPM = (velocidade / PPR) * 60

  // Converte o tempo para segundos
  float timeInSeconds = currentTime / 1000000.0;

  // Exibe a velocidade calculada em RPM e o tempo no Serial Monitor
  Serial.print("Tempo: ");
  Serial.print(timeInSeconds, 6); // Tempo em segundos com 6 casas decimais
  Serial.print(" s, Velocidade: ");
  Serial.print(rpm);
  Serial.println(" RPM");
}

void setup() {
  // Configura os pinos como saída ou entrada conforme necessário
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(CHA, INPUT);
  pinMode(CHB, INPUT);

  // Inicializa a comunicação serial
  Serial.begin(9600);

  // Configura interrupção para contar os pulsos do encoder
  attachInterrupt(digitalPinToInterrupt(CHA), countPulses, RISING);

  // Define a direção do motor (sentido horário)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
}

void loop() {
  // Define a razão cíclica inicial como 0
  currentDutyCycle = MIN_DUTY_CYCLE;
  analogWrite(ENA, currentDutyCycle * 255);

  // Aguarda a estabilização
  delay(2000); // Espera 2 segundos para estabilizar

  // Gradualmente aumenta a razão cíclica de MIN_DUTY_CYCLE para MAX_DUTY_CYCLE
  for (currentDutyCycle = MIN_DUTY_CYCLE; currentDutyCycle <= MAX_DUTY_CYCLE; currentDutyCycle += 0.01) {
    analogWrite(ENA, currentDutyCycle * 255);
    calculateCurrentSpeed();
    delay(200); // Espera 200 ms entre cada incremento
  }

  // Mantém a razão cíclica constante no valor máximo
  while (true) {
    // Mantém a razão cíclica constante
    analogWrite(ENA, MAX_DUTY_CYCLE * 255);

    // Calcula e exibe a velocidade estabilizada
    calculateCurrentSpeed();

    // Espera para evitar leituras muito frequentes
    delay(100);
  }
}
