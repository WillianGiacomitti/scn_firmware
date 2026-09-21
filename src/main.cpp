#include <Arduino.h>
#include <ESP32Servo.h>

// Definição dos pinos (verifique onde você conectou no seu ESP32)
const int PIN_SERVO_ZOOM = 18;
const int PIN_SERVO_SHOT = 19;

// Criação dos objetos para os servos
Servo servoZoom;
Servo servoShot;

// Variáveis para comunicação Serial
String serialBuffer = "";

// Função responsável por interpretar o protocolo
void processarComando(String comando) {
  comando.trim(); // Remove espaços em branco acidentais
  comando.toUpperCase(); // Padroniza para maiúsculo para evitar erros
  
  // Separar o ALVO da AÇÃO baseado no caractere ':'
  int separadorIndex = comando.indexOf(':');
  
  if (separadorIndex == -1) {
    Serial.println("ERRO: Formato invalido. Use ALVO:ACAO");
    return;
  }

  String alvo = comando.substring(0, separadorIndex);
  String acao = comando.substring(separadorIndex + 1);

  // Lógica de roteamento dos comandos
  if (alvo == "ZOOM") {
    if (acao == "IN") {
      servoZoom.write(115); // Ajuste o grau de zoom in conforme sua lente
      delay(500);
      servoZoom.write(95);
      Serial.println("OK: Zoom IN acionado");
    } 
    else if (acao == "OUT") {
      servoZoom.write(75);  // Ajuste o grau de zoom out conforme sua lente
      delay(500);
      servoZoom.write(95);
      Serial.println("OK: Zoom OUT acionado");
    } 
    else if (acao == "RESET") {
      servoZoom.write(95);
      Serial.println("OK: Zoom voltou a 90 graus");
    } 
    else {
      Serial.println("ERRO: Acao de ZOOM desconhecida");
    }
  } 
  
  else if (alvo == "SHOT") {
    if (acao == "CLICK") {
      Serial.println("OK: Disparando camera...");
      servoShot.write(140); // Move para pressionar o botão
      delay(1000);           // Aguarda 300ms (tempo de clique)
      servoShot.write(145);  // Retorna para soltar o botão
      delay(500);           // 
      servoShot.write(90);  // Retorna para soltar o botão
      Serial.println("OK: Disparo concluido");
    } 
    else {
      Serial.println("ERRO: Acao de SHOT desconhecida");
    }
  } 
  
  else {
    Serial.println("ERRO: Alvo desconhecido (Use ZOOM ou SHOT)");
  }
}

void setup() {
  Serial.begin(115200);
  delay(5000); // Pequena pausa para garantir que a Serial esteja pronta
  
  // O ESP32Servo precisa ter os timers alocados
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  // Anexa os servos aos pinos
  // Os valores 500 e 2400 são os pulsos min/max padrão para servos como o SG92R
  servoZoom.setPeriodHertz(50);
  servoZoom.attach(PIN_SERVO_ZOOM, 500, 2400);
  
  servoShot.setPeriodHertz(50);
  servoShot.attach(PIN_SERVO_SHOT, 500, 2400);

  // Inicializa ambos na referência de 90 graus
  servoZoom.write(95);
  servoShot.write(90);
  
  Serial.println("Sistema Iniciado. Servos em 90 graus.");
  Serial.println("Aguardando comandos (ex: ZOOM:IN, SHOT:CLICK)...");
}

void loop() {
  // Leitura Serial não-bloqueante (robusta para escalabilidade)
  while (Serial.available() > 0) {
    char c = Serial.read();
    
    // Se receber o fim do comando (quebra de linha)
    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        processarComando(serialBuffer);
        serialBuffer = ""; // Limpa o buffer para o próximo comando
      }
    } else {
      serialBuffer += c; // Adiciona o caractere ao buffer
    }
  }
}

