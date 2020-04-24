#!/usr/bin/env python3
from flask import Flask, Response
from flask_cors import CORS
from flask import render_template
import flask

app = Flask(__name__)

light_filename = "light.csv"
air_temp_filename = "air_temp.csv"

def get_current_value(filename):
   # Get last line of each value
   with open("../" + filename, 'r') as f:
      for line in f:
         pass
      value = line.split(',')[-1]
      return value

@app.route('/garden')
def garden():
   air_temp = None
   light = None

   light = get_current_value(light_filename)
   air_temp = get_current_value(air_temp_filename)

   return render_template('garden.html', air_temp=air_temp, light=light)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
