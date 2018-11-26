# -*- coding: utf8 -*-
import os
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

from blockchain import Blockchain
from db import EmotionalDB

os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "bockchaincontroller"
os.environ['DBNAME'] = "bockchain"
os.environ['DBPASS'] = "supersecretpass"

emotional_db_writer_config = {
                            "DBHOST":os.environ['DBHOST'],
                            "DBUSER":os.environ['DBUSER'],
                            "DBNAME":os.environ['DBNAME'],
                            "DBPASS":os.environ['DBPASS']
                            }

tables_create_commands = [
                        """
                        CREATE TABLE block (
                            id INTEGER PRIMARY KEY,
                            creditor VARCHAR(255),
                            recipient VARCHAR(255),
                            amount VARCHAR(255),
                            hash VARCHAR(255),
                            before_id INTEGER,
                            CONSTRAINT block_before_id_fkey FOREIGN KEY (before_id)
                                REFERENCES block (id)
                        )
                        """,
                        """
                        CREATE TABLE group_emot (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255)
                        )
                        """,
                        """
                        CREATE TABLE user_emot (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255),
                            registration_date VARCHAR(255),
                            group_id INTEGER,
                            CONSTRAINT user_group_id_fkey FOREIGN KEY (group_id)
                                REFERENCES group_emot (id)
                        )
                        """,
                        """
                        CREATE TABLE feeling (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255)
                        )
                        """,
                        """
                        CREATE TABLE emotion (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255)
                        )
                        """,
                        """
                        CREATE TABLE actual_feeling (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            feeling_id INTEGER,
                            feeling_object VARCHAR(255),
                            intensity INTEGER,
                            time timestamp,
                            CONSTRAINT actual_feeling_id_fkey FOREIGN KEY (feeling_id)
                                REFERENCES feeling (id),
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        )
                        """,
                        """
                        CREATE TABLE actual_emotion (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            emotion_id INTEGER,
                            intensity INTEGER,
                            time timestamp,
                            CONSTRAINT Actual_emotion_id_fkey FOREIGN KEY (emotion_id)
                                REFERENCES emotion (id),
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        )
                        """,
                        """
                        CREATE TABLE user_state (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            time timestamp,
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        )
                        """,
                        """
                        CREATE TABLE event (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            time timestamp,
                            place VARCHAR(255),
                            description VARCHAR(255),
                            user_state_before_id INTEGER,
                            user_state_after_id INTEGER,
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id),
                            CONSTRAINT user_state_before_id_fkey FOREIGN KEY (user_state_before_id)
                                REFERENCES user_state (id),
                            CONSTRAINT user_state_after_id_fkey FOREIGN KEY (user_state_after_id)
                                REFERENCES user_state (id)
                        )
                        """,
                        """
                        CREATE TABLE tip (
                            id INTEGER PRIMARY KEY,
                            user_state_id INTEGER,
                            name VARCHAR(255),
                            description VARCHAR(255),
                            CONSTRAINT user_state_id_fkey FOREIGN KEY (user_state_id)
                                REFERENCES user_state (id)
                        )
                        """
                        ]

tables_delete_commands = [
                        """
                        DROP TABLE actual_feeling
                        """,
                        """
                        DROP TABLE actual_emotion
                        """,
                        """
                        DROP TABLE block CASCADE
                        """,
                        """
                        DROP TABLE feeling
                        """,
                        """
                        DROP TABLE emotion
                        """,
                        """
                        DROP TABLE tip
                        """,
                        """
                        DROP TABLE event
                        """,
                        """
                        DROP TABLE user_state CASCADE
                        """,
                        """
                        DROP TABLE user_emot CASCADE
                        """,
                        """
                        DROP TABLE group_emot
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