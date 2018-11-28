# -*- coding: utf8 -*-
import os
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

from blockchain import Blockchain
from db import EmotionalDB

#os.environ['DBHOST'] = "localhost"
#os.environ['DBUSER'] = "bockchaincontroller"
#os.environ['DBNAME'] = "bockchain"
#os.environ['DBPASS'] = "supersecretpass"

emotional_db_writer_config = {
                            "DBHOST":os.environ['DBHOST'],
                            "DBUSER":os.environ['DBUSER'],
                            "DBNAME":os.environ['DBNAME'],
                            "DBPASS":os.environ['DBPASS']
                            }

tables_create_commands = [
                        # DROP tables, functions and triggers
                        """
                        DROP TABLE actual_feeling;
                        DROP TABLE actual_emotion;
                        DROP TABLE block CASCADE;
                        DROP TABLE feeling;
                        DROP TABLE emotion;
                        DROP TABLE tip;
                        DROP TABLE event;
                        DROP TABLE user_state CASCADE;
                        DROP TABLE user_emot CASCADE;
                        DROP TABLE group_emot;

                        DROP TRIGGER IF EXISTS event_stamp_tr ON event;
                        DROP FUNCTION IF EXISTS event_stamp;
                        """,
                        # Create tables
                        """
                        CREATE TABLE block (
                            id SERIAL PRIMARY KEY,
                            creditor VARCHAR(255),
                            recipient VARCHAR(255),
                            amount VARCHAR(255),
                            hash VARCHAR(255),
                            before_id INTEGER,
                            CONSTRAINT block_before_id_fkey FOREIGN KEY (before_id)
                                REFERENCES block (id)
                        );
                        CREATE TABLE group_emot(
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255)
                        );
                        CREATE TABLE user_emot (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255),
                            passhash VARCHAR(255),
                            registration_date VARCHAR(255),
                            group_id INTEGER,
                            CONSTRAINT user_group_id_fkey FOREIGN KEY (group_id)
                                REFERENCES group_emot (id)
                        );
                        CREATE TABLE feeling (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255)
                        );
                        CREATE TABLE emotion (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255)
                        );
                        CREATE TABLE actual_feeling (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            feeling_id INTEGER,
                            feeling_object VARCHAR(255),
                            intensity INTEGER CHECK (intensity > 0 and intensity <= 10),
                            time timestamp,
                            CONSTRAINT actual_feeling_id_fkey FOREIGN KEY (feeling_id)
                                REFERENCES feeling (id),
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        );
                        CREATE TABLE actual_emotion (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            emotion_id INTEGER,
                            intensity INTEGER,
                            time timestamp,
                            CONSTRAINT Actual_emotion_id_fkey FOREIGN KEY (emotion_id)
                                REFERENCES emotion (id),
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        );
                        CREATE TABLE user_state (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            time timestamp,
                            CONSTRAINT user_id_fkey FOREIGN KEY (user_id)
                                REFERENCES user_emot (id)
                        );
                        CREATE TABLE event (
                            id SERIAL PRIMARY KEY,
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
                        );
                        CREATE TABLE tip (
                            id SERIAL PRIMARY KEY,
                            user_state_id INTEGER,
                            name VARCHAR(255),
                            description VARCHAR(255),
                            CONSTRAINT user_state_id_fkey FOREIGN KEY (user_state_id)
                                REFERENCES user_state (id)
                        );
                        """,
                        # Create triggers
                        """
                        CREATE OR REPLACE FUNCTION event_stamp() 
                            RETURNS trigger AS $event_stamp$
                                BEGIN
                                    -- Проверка, что указан пользователь и описание события
                                    IF NEW.user_id IS NULL THEN
                                        RAISE EXCEPTION 'user_id cannot be null';
                                    END IF;
                                    IF NEW.description IS NULL THEN
                                        RAISE EXCEPTION 'description cannot be null';
                                    END IF;

                                    -- Установка даты записи
                                    NEW.time := current_timestamp;
                                    RETURN NEW;
                                END;
                            $event_stamp$ LANGUAGE plpgsql;

                        CREATE TRIGGER event_stamp_tr BEFORE INSERT OR UPDATE ON event
                            FOR EACH ROW EXECUTE PROCEDURE event_stamp();
                        """,
                        # Insert data
                        '''
                        INSERT INTO block (id, creditor, recipient, amount, hash) 
                            VALUES (1, 'GENESIS BLOCK C', 'GENESIS BLOCK R', 'GENESIS BLOCK A', 'GENESIS BLOCK HASH');

                        INSERT INTO user_emot (id, name, registration_date) 
                            VALUES  
                                (1, 'Aleks', current_timestamp),
                                (2, 'Natasha', current_timestamp);

                        INSERT INTO feeling (id, name) 
                            VALUES 	
                                (1, 'joy'),
                                (2, 'trust'),
                                (3, 'anger'),
                                (4, 'anticipation'),
                                (5, 'disgust'),
                                (6, 'sadness'),
                                (7, 'surprise'),
                                (8, 'fear');

                        INSERT INTO emotion (id, name) 
                            VALUES 	
                                (1, 'extasy'),
                                (2, 'vigilance'),
                                (3, 'rage'),
                                (4, 'loathing'),
                                (5, 'grief'),
                                (6, 'amazement'),
                                (7, 'terror'),
                                (8, 'admiration');

                        INSERT INTO actual_feeling (user_id, feeling_id, feeling_object, intensity, time)
	                        VALUES 
                                (1, 1, 'Work', 10, current_timestamp),
                                (2, 1, 'Work', 10, current_timestamp),
                                (1, 3, 'Eat', 10, current_timestamp),
                                (1, 2, 'Wearpon', 1, current_timestamp),
                                (1, 1, 'Work', 10, current_timestamp),
                                (2, 1, 'Work', 10, current_timestamp),
                                (1, 3, 'Eat', 10, current_timestamp),
                                (1, 2, 'Wearpon', 1, current_timestamp),
                                (1, 1, 'Work', 10, current_timestamp),
                                (2, 1, 'Work', 10, current_timestamp),
                                (1, 3, 'Eat', 10, current_timestamp),
                                (1, 2, 'Wearpon', 1, current_timestamp),
                                (1, 1, 'Work', 10, current_timestamp),
                                (2, 1, 'Work', 10, current_timestamp),
                                (1, 3, 'Eat', 10, current_timestamp),
                                (1, 2, 'Wearpon', 1, current_timestamp),
                                (1, 1, 'DB', 10, current_timestamp);
                                

                        INSERT INTO event (id, user_id, description) 
                            VALUES (2, 1, 'hello');
                        '''
                        ]

tables_delete_commands = []

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


# Emotional
feelings = ['joy','trust', 'anger','anticipation','disgust','sadness','surprise','fear']
@app.route('/emotional', methods=['GET', 'POST'])
def emotional_index():
    if request.method == 'POST':
        feeling = request.form['feeling']
        user = request.form['user']
        
        if user == 'Aleks' or user == 'Natasha':
            querry =    '''
                            SELECT * 
                            FROM actual_feeling 
                            JOIN user_emot ON user_emot.id = actual_feeling.user_id
                            WHERE user_emot.name = '{}'
                        '''.format(user)
            result = emot_db.select(command=querry)
        else: 
            result = []

        return render_template('emotional_index.html', feelings=feelings, data=result)

    return render_template('emotional_index.html', feelings=feelings)

if __name__ == "__main__":
    app.run(debug=True)