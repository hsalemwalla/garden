#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <avr/sleep.h>

#include "arduino_secrets.h"

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

const char broker[] = "192.168.1.65";
const int port = 1883;

// Values and functions for calibrating the various sensors

// Soil moisture
int PIN_SOIL_MOISTURE = A0;
int SOIL_MOISTURE_MAX = 306.9; // 100% Moisture (1.50V)
int SOIL_MOISTURE_MIN = 519; // 0% Moisture (2.54V)
char TOPIC_SOIL_MOISTURE[] = "garden/soil/moisture";
int processSoilMoisture(int raw) {
  // returns percentage moisture
  int constrained = constrain(raw, SOIL_MOISTURE_MAX, SOIL_MOISTURE_MIN);
  int moisture = map(constrained, SOIL_MOISTURE_MIN, SOIL_MOISTURE_MAX, 0, 100);
  return moisture;
}

// Air temperature
int PIN_AIR_TEMP = A1;
int AIR_TEMP_MAX = 1024 ;
int AIR_TEMP_MIN = 0;
char TOPIC_AIR_TEMP[] = "garden/air/temperature";


// Light
int PIN_LIGHT = A2;
int LIGHT_MAX = 491;
int LIGHT_MIN = 8;
char TOPIC_LIGHT[] = "garden/light";
int processLight(int raw) {
  // returns percentage moisture
  int constrained = constrain(raw, LIGHT_MIN, LIGHT_MAX);
  int light = map(constrained, LIGHT_MIN, LIGHT_MAX, 0, 100);
  return light;
}

// Setup functions

void wifiSetup() {
  Serial.print("Attempting to connect to ");
  Serial.print(ssid);
  Serial.print("...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(5000);
  }
  Serial.println("Connected!");
  Serial.println();
}

void sensorsSetup() {
  pinMode(PIN_SOIL_MOISTURE, INPUT);
  pinMode(PIN_AIR_TEMP, INPUT);
  pinMode(PIN_LIGHT, INPUT);
}

void mqttSetup() {
  Serial.print("Attempting to connect to broker ");
  Serial.print(broker);
  Serial.print("...");
  if (!mqttClient.connect(broker, port)) {
    Serial.print("Failed, error code: ");
    Serial.println(mqttClient.connectError());
    while (1);
  }
  Serial.println("Connected!");
  Serial.println();
}

void mqttSend(char topic[], int msg) {
  mqttClient.beginMessage(topic);
  mqttClient.print(msg);
  mqttClient.endMessage();
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {}

  wifiSetup();
  mqttSetup();
  sensorsSetup();

  //lowPowerModeSetup();
}

void loop() {
  // Read sensor values
  // Sleep for a while
  int soilMoisture;
  int airTemp;
  int light; 

  // Soil moisture 
  soilMoisture = processSoilMoisture(analogRead(PIN_SOIL_MOISTURE));
  Serial.print("Soil moisture: ");
  Serial.print(soilMoisture);
  Serial.println("%");
  mqttSend(TOPIC_SOIL_MOISTURE, soilMoisture);

  // Air temp
  // TODO
  
  // Light
  light = processLight(analogRead(PIN_LIGHT));
  Serial.print("Light: ");
  Serial.println(light);
  mqttSend(TOPIC_LIGHT, light);


  delay(5000);

}
