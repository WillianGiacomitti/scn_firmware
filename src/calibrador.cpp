#include <Arduino.h>
#include <ESP32Servo.h>

const int PIN_SERVO_ZOOM = 18;
const int PIN_SERVO_SHOT = 19;

Servo servoZoom;
Servo servoShot;
String serialBuffer = "";

void processarComando(String comando) {
  comando.trim(); 
  comando.toUpperCase(); 
  
  int separadorIndex = comando.indexOf(':');
  if (separadorIndex == -1) return; // Ignora se não tiver o ":"

  String alvo = comando.substring(0, separadorIndex);
  String acao = comando.substring(separadorIndex + 1);

  // Converte o que veio depois dos dois pontos para número
  int angulo = acao.toInt();

  // Trava de segurança para não forçar o servo além do limite físico
  if (angulo < 0) angulo = 0;
  if (angulo > 180) angulo = 180;

  if (alvo == "ZOOM") {
    servoZoom.write(angulo);
    Serial.println("ZOOM movido para: " + String(angulo));
  } 
  else if (alvo == "SHOT") {
    servoShot.write(angulo);
    Serial.println("SHOT movido para: " + String(angulo));
  }
}

void setup() {
  Serial.begin(115200);
  
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  servoZoom.setPeriodHertz(50);
  servoZoom.attach(PIN_SERVO_ZOOM, 500, 2400);
  
  servoShot.setPeriodHertz(50);
  servoShot.attach(PIN_SERVO_SHOT, 500, 2400);

  // Inicializa ambos na referência de 90 graus
  servoZoom.write(90);
  servoShot.write(90);
  
  Serial.println("Modo de Calibracao Iniciado.");
  Serial.println("Envie comandos como ZOOM:120 ou SHOT:45");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (serialBuffer.length() > 0) {
        processarComando(serialBuffer);
        serialBuffer = ""; 
      }
    } else {
      serialBuffer += c; 
    }
  }
}

