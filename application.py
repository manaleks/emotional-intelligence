# -*- coding: utf8 -*-
import os
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

from blockchain import Blockchain
from db import EmotionalDB

emotional_db_writer_config = {
                            "DBHOST":os.environ['DBHOST'],
                            "DBUSER":os.environ['DBUSER'],
                            "DBNAME":os.environ['DBNAME'],
                            "DBPASS":os.environ['DBPASS']
                            }

tables_create_commands = [
                        """
                        CREATE TABLE Block (
                            id INTEGER PRIMARY KEY,
                            creditor VARCHAR(255),
                            recipient VARCHAR(255),
                            amount VARCHAR(255),
                            hash VARCHAR(255),
                            before_id INTEGER,
                            CONSTRAINT block_before_id_fkey FOREIGN KEY (before_id)
                                REFERENCES Block (id)
                        )
                        """
                        ]

tables_delete_commands = [
                        """
                        DROP TABLE block
                        """
                        ]

emot_db = EmotionalDB(emotional_db_writer_config, tables_delete_commands, tables_create_commands)
emot_db.create_table()

B_chain = Blockchain(emot_db)


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

        B_chain.write_block(name=lender, amount=amount, to_whom=borrower, hash='')
    return render_template('blockchain_index.html')

@app.route('/blockchain/checking', methods=['GET'])
def blockchain_check():
    results = B_chain.check_integrity()
    return render_template('blockchain_index.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)