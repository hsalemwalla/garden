#!/usr/bin/env python

import paho.mqtt.client as mqtt #import the client1
import time

def on_message(client, userdata, message):
   print(message.topic + ": " + str(message.payload.decode("utf-8")))

broker_address="localhost"

client = mqtt.Client("Garden server")
client.on_message=on_message 
client.connect(broker_address)
client.subscribe("garden/temp")
client.loop_forever()
