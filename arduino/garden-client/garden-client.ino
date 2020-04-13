#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include <avr/sleep.h>
#include <OneWire.h> 
#include <DallasTemperature.h>


#include "arduino_secrets.h"

#define VERSION "1.0.0"

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
char MQTT_CLIENT_ID[] = "Gardener";
const char broker[] = "192.168.1.65";
const int port = 1883;

// Values and functions for calibrating the various sensors

// Soil moisture
int PIN_SOIL_MOISTURE = A1;
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
int PIN_AIR_TEMP = 2; // Digital 2
char TOPIC_AIR_TEMP[] = "garden/air/temperature";
OneWire airTempWire(PIN_AIR_TEMP);
DallasTemperature airTempSensor(&airTempWire);

// Light
int PIN_LIGHT = A0;
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
}

void sensorsSetup() {
  pinMode(PIN_SOIL_MOISTURE, INPUT);
  pinMode(PIN_LIGHT, INPUT);
  airTempSensor.begin();

}

void mqttConnect() {
  Serial.print("Attempting to connect to broker ");
  Serial.print(broker);
  Serial.print("...");
  if (!mqttClient.connect(broker, port)) {
    Serial.print("Failed, error code: ");
    Serial.println(mqttClient.connectError());
    while (1);
  }
  Serial.println("Connected!");
}

void mqttSend(char topic[], int msg) {
  mqttClient.beginMessage(topic);
  mqttClient.print(msg);
  mqttClient.endMessage();
}

void setup() {
  Serial.begin(9600);
  while (!Serial) {}
  Serial.print("Version: ");
  Serial.println(VERSION);

  pinMode(LED_BUILTIN,OUTPUT);
  
  wifiSetup();
  mqttClient.setId(MQTT_CLIENT_ID);
  mqttConnect();
  sensorsSetup();

  digitalWrite(LED_BUILTIN,HIGH);

  //lowPowerModeSetup();
  Serial.println();
}

// vars for sensor readings
int soilMoisture;
int airTemp;
int light;
int debug = true;

void loop() {

  if (!mqttClient.connected()) {
    // MQTT client is disconnected, connect
    mqttConnect();
  }

  // Soil moisture 
  /********************************************************************/
  soilMoisture = processSoilMoisture(analogRead(PIN_SOIL_MOISTURE));
  Serial.print("Soil moisture: ");
  Serial.print(soilMoisture);
  Serial.println("%");
  mqttSend(TOPIC_SOIL_MOISTURE, soilMoisture);

  // Air temp
  /********************************************************************/
  airTempSensor.requestTemperatures(); // Send the command to get temperature readings 
  airTemp = airTempSensor.getTempCByIndex(0);
  Serial.print("Air temperature is: "); 
  Serial.println(airTemp);  // Only one sensor
  mqttSend(TOPIC_AIR_TEMP, airTemp);

  // Light
  /********************************************************************/
  light = processLight(analogRead(PIN_LIGHT));
  Serial.print("Light: ");
  Serial.println(light);
  mqttSend(TOPIC_LIGHT, light);

  // Delay for 5 mins
  for (int i = 0; i < 30; i++) {
    // 30 second loops 10 times so we don't timeout on the broker
    delay(10000);
    Serial.println("Polling broker");
    if (debug == true) {
      long rssi = WiFi.RSSI();
      mqttSend("garden/debug/rssi", (int)rssi);
    }
    mqttClient.poll();
  }
  Serial.println();
}
