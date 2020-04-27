#!/usr/bin/env python3
from flask import Flask, Response
from flask import render_template
import flask
import os

app = Flask("Garden")
app.root_path = os.path.dirname(os.path.abspath(__file__))


light_filename = "light.csv"
air_temp_filename = "air_temp.csv"

def get_status():
   with open("/home/pi/development/garden/server/status", 'r') as f:
      status = f.readline()
   return status


def get_current_value(filename):
   # Get last line of each value
   with open("/home/pi/development/garden/server/" + filename, 'r') as f:
      for line in f:
         pass
      value = line.split(',')[-1]
      return value

@app.route('/')
def garden():
   ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
   print(ROOT_DIR)

   status = get_status()
   light = get_current_value(light_filename)
   air_temp = get_current_value(air_temp_filename)

   return render_template('garden.html', air_temp=air_temp, light=light, status=status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
