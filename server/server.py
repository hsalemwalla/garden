#!/usr/bin/env python

import paho.mqtt.client as mqtt 
import time
import argparse

BROKER_ADDRESS="localhost"
CLIENT_NAME = "Garden server"
debug = False


# Util {{{
#############################################################
def log(msg):
   if debug:
      print(msg)
############################################################# }}}

# Topic Handlers {{{
#############################################################

def write_msg_to_file(line, filename):
   if not debug: 
      with open(filename, "w+") as f:
         f.write(line)

def get_current_date_string():
   return time.strftime("%d/%m/%Y", time.localtime())

def get_current_time_string():
   return time.strftime("%H:%M:%S", time.localtime())

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
   log("message recvd: " + message.topic + ": " + str(message.payload.decode("utf-8")))
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
          'garden/light': handle_light }

def main():
   log("Client name: " + CLIENT_NAME)
   log("Broker address: " + BROKER_ADDRESS)
   log("")
   client = mqtt.Client(CLIENT_NAME)

   client.on_message=on_message 
   client.on_connect=on_connect 
   client.on_disconnect=on_disconnect 

   client.connect(BROKER_ADDRESS)

   # We can either loop forever blocking:
   #   client.loop_forever()
   # start the loop in diff thread:
   #   client.loop_start()
   #   client.loop_stop()
   # Or loop manually (blocking with timeout)
   #   client.loop(timeout)
   log("Beginning mqtt loop")
   while(True):
      client.loop(0.1)


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='Garden server')
   parser.add_argument('--debug', action='store_true', help='Turn debug mode on')
   args = parser.parse_args()
   if args.debug:
      print("---------------------------------------------------")
      print("Debug mode ON")
      print("Print statements enabled, writing to files disabled")
      print("---------------------------------------------------")
   debug = args.debug

   main()
