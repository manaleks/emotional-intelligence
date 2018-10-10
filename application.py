# -*- coding: utf8 -*-
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

import blockchain

app = Flask(__name__)

# Emotional Intelligence
def main_page():
    return render_template('main.html')

# Emotional Intelligence
def simple_text():
    return "Hello!"

rules = []
rules.append({"rule":'/',"name":"main_page","method":main_page})
rules.append({"rule":'/simple_text',"name":"simple_text","method":simple_text})
for rule in rules:
    app.add_url_rule(rule["rule"], rule["name"], rule["method"])

# BLOCKCHAIN
@app.route('/blockchain', methods=['GET', 'POST'])
def blockchain_index():
    if request.method == 'POST':
        lender = request.form['lender']
        amount = request.form['amount']
        borrower = request.form['borrower']

        blockchain.write_block(name=lender, amount=amount, to_whom=borrower, hash='')
    return render_template('blockchain_index.html')

@app.route('/blockchain/checking', methods=['GET'])
def blockchain_check():
    results = blockchain.check_integrity()
    return render_template('blockchain_index.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)