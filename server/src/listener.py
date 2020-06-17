#!/usr/bin/env python3

import time
import argparse
import math

import paho.mqtt.client as mqtt 

STATUS_OK="OK"
STATUS_NO_COMM_FROM_ARDUINO="NO_COMM"
STATUS_SERVER_ERROR="SERVER_ERROR"
status = None

remote = False
BROKER_ADDRESS="localhost"

CLIENT_NAME = "Garden server"
debug = False

light_enabled = True
air_temp_enabled = True
soil_moisture_enabled = True

last_message_time = -math.inf

# Util {{{
#############################################################
def log(msg):
   if debug:
      print(msg)

def write_msg_to_file(line, filename):
   if not debug: 
      with open(filename, "a") as f:
         f.write(line)

def get_time_string(t):
   return time.strftime("%m/%d/%Y %H:%M:%S", t)

def get_current_date_string():
   return time.strftime("%m/%d/%Y", time.localtime())

def get_current_time_string():
   return time.strftime("%H:%M:%S", time.localtime())

def update_status_file(sts):
   with open("status", "w+") as f:
      f.write(sts)

def set_status(sts):
   global status
   if status == sts:
      pass
   else:
      status = sts
      log("Changing status to: " + sts)
      update_status_file(sts)

############################################################# }}}

# Topic Handlers {{{
#############################################################

def handle_light(message):
   log("handle_light")
   filename = "light.csv"
   date = get_current_date_string()
   time = get_current_time_string()
   msg = message.payload.decode("utf-8")
   line = date + "," + time + "," + msg + "\n"
   write_msg_to_file(line, filename)

def handle_air_temp(message):
   log("handle_air_temp")
   filename = "air_temp.csv"
   date = get_current_date_string()
   time = get_current_time_string()
   msg = message.payload.decode("utf-8")
   line = date + "," + time + "," + msg + "\n"
   write_msg_to_file(line, filename)

def handle_soil_moisture(message):
   log("handle_soil_moisture")
   filename = "soil_mosture.csv"
   date = get_current_date_string()
   time = get_current_time_string()
   msg = message.payload.decode("utf-8")
   line = date + "," + time + "," + msg + "\n"
   if soil_moisture_enabled:
      write_msg_to_file(line, filename)

def handle_debug(message):
   log("handle_debug")
   filename = "debug.csv"
   date = get_current_date_string()
   time = get_current_time_string()
   msg = message.payload.decode("utf-8")
   line = date + "," + time + "," + msg + "\n"
   write_msg_to_file(line, filename)

############################################################# }}}

# MQTT Handlers {{{
#############################################################
def on_connect(client, userdata, flags, rc):
   print("\"" + client._client_id.decode("utf-8") + "\" connected successfully")
   # Subscribe to the topics
   for topic in TOPICS:
      print("Subscribing to: " + topic)
      client.subscribe(topic)

def on_disconnect(client, userdata, flags, rc):
   print("\"" + client._client_id.decode("utf-8") + "\" disconnected successfully")
   client.loop_stop()

def on_message(client, userdata, message):
   global last_message_time
   last_message_time = time.time()
   log(get_time_string(last_message_time) + ": " + message.topic + ": " + str(message.payload.decode("utf-8")))
   # We have received something from the arduino, so all is good
   set_status(STATUS_OK)

   handler = None
   for topic in TOPICS: 
      if topic == message.topic:
         handler = TOPICS[topic]

   if handler is None:
      log("Unknown topic")
   else:
      handler(message)

############################################################# }}}

TOPICS = {'garden/soil/moisture': handle_soil_moisture,
          'garden/air/temperature': handle_air_temp,
          'garden/light': handle_light, 
          'garden/debug/#': handle_debug }

def main():
   log("Client name: " + CLIENT_NAME)
   log("Broker address: " + BROKER_ADDRESS)
   log("")
   client = mqtt.Client(CLIENT_NAME)

   client.on_message=on_message 
   client.on_connect=on_connect 
   client.on_disconnect=on_disconnect 

   client.connect(BROKER_ADDRESS)
   set_status(STATUS_OK)

   # We can either loop forever blocking:
   #   client.loop_forever()
   # start the loop in diff thread:
   #   client.loop_start()
   #   client.loop_stop()
   # Or loop manually (blocking with timeout)
   #   client.loop(timeout)
   log("Beginning mqtt loop")
   while(True):
      try:
         current_time = time.time()
         # If the last message was recvd more than 10 mins ago
         if last_message_time is not None:
            if current_time > last_message_time + (60*10):
               set_status(STATUS_NO_COMM_FROM_ARDUINO)
         client.loop(0.1)
      except e:
         print("Error occured");
         set_status(STATUS_SERVER_ERROR)
         break;


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Garden server')
   parser.add_argument('--debug', action='store_true', help='Turn debug mode on')
   parser.add_argument('--remote', action='store_true', help='MQTT Broker is on remote device')
   parser.add_argument('--no-soil-moisture', action='store_true', help='Soil moisture sensor is disabled')
   parser.add_argument('--no-light', action='store_true', help='Light sensor is disabled')
   parser.add_argument('--no-air-temp', action='store_true', help='Air temp sensor is disabled')
   args = parser.parse_args()
   if args.debug:
      print("---------------------------------------------------")
      print("Debug mode ON")
      print("Print statements enabled, writing to files disabled")
      print("---------------------------------------------------")
   debug = args.debug
   remote = args.remote
   if remote:
      BROKER_ADDRESS = "server.local"

   # If flags set, disable sensor
   soil_moisture_enabled = not args.no_soil_moisture
   light_enabled = not args.no_light
   air_temp_enabled = not args.no_air_temp

   print("Sensors enabled:")
   print("Soil moisture:",soil_moisture_enabled)
   print("Light:",light_enabled)
   print("Air temperature:",air_temp_enabled)
   print()

   main()
