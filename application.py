# -*- coding: utf8 -*-
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

app = Flask(__name__)

# Emotional Intelligence
@app.route('/', methods=['GET'])
def main_page():
    return render_template('main.html')

# Emotional Intelligence
@app.route('/simple_text', methods=['GET'])
def simple_text():
    return "Hello!"

if __name__ == "__main__":
    app.run(debug=True)