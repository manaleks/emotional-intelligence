# -*- coding: utf8 -*-
import os
from flask import Flask, request, render_template
try:
  import simplejson as json
except:
  import json

from blockchain import Blockchain
from db import EmotionalDB

"""
os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "bockchaincontroller"
os.environ['DBNAME'] = "bockchain"
os.environ['DBPASS'] = "supersecretpass"
"""

emotional_db_writer_config = {
                            "DBHOST":os.environ['DBHOST'],
                            "DBUSER":os.environ['DBUSER'],
                            "DBNAME":os.environ['DBNAME'],
                            "DBPASS":os.environ['DBPASS']
                            }

create_commands = [
                    # Blockchain database work
                    '''
                    DROP TABLE IF EXISTS block;
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
                    INSERT INTO block (id, creditor, recipient, amount, hash) 
                    VALUES (1, 'GENESIS BLOCK C', 'GENESIS BLOCK R', 'GENESIS BLOCK A', 'GENESIS BLOCK HASH');
                    ''',
                    # DROP tables, functions and triggers
                    """
                    DROP TRIGGER IF EXISTS event_stamp_tr ON event;
                    DROP FUNCTION IF EXISTS event_stamp();
                    DROP FUNCTION IF EXISTS get_report(user_name text);

                    DROP TABLE IF EXISTS event_tag;
                    DROP TABLE IF EXISTS actual_feeling_tag;
                    DROP TABLE IF EXISTS feeling_object_tag;
                    DROP TABLE IF EXISTS tag;
                    DROP TABLE IF EXISTS event;
                    DROP TABLE IF EXISTS actual_feeling;
                    DROP TABLE IF EXISTS feeling_object;
                    DROP TABLE IF EXISTS emotional_user;
                    DROP TABLE IF EXISTS feeling;
                    DROP TABLE IF EXISTS color;
                    """
                    # Create tables
                    """
                    CREATE TABLE color (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(20),
                        code VARCHAR(10)
                    );
                    CREATE TABLE feeling (
                        id SERIAL PRIMARY KEY,
                        color_id SMALLINT,
                        name VARCHAR(20),
                        CONSTRAINT feeling_color_id_fkey FOREIGN KEY (color_id)
                            REFERENCES color (id)
                    );
                    CREATE TABLE emotional_user (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100),
                        pass_hash VARCHAR(100),
                        email VARCHAR(100) UNIQUE,
                        registration_date timestamp
                    );
                    CREATE TABLE feeling_object (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        name VARCHAR(20),
                        CONSTRAINT feeling_object_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id)
                    );
                    CREATE TABLE actual_feeling (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        feeling_id SMALLINT,
                        feeling_object_id INTEGER,
                        intensity INTEGER CHECK (intensity > 0 and intensity <= 10),
                        time timestamp,
                        CONSTRAINT actual_feeling_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        CONSTRAINT actual_feeling_feeling_id_fkey FOREIGN KEY (feeling_id)
                        REFERENCES feeling (id),
                        CONSTRAINT actual_feeling_feeling_object_id_fkey FOREIGN KEY (feeling_object_id)
                        REFERENCES feeling_object (id)
                    );
                    CREATE TABLE event (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        feeling_before_id INTEGER,
                        feeling_after_id INTEGER,
                        name VARCHAR(100),
                        time timestamp,
                        place VARCHAR(100),
                        description VARCHAR(255),
                        CONSTRAINT event_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        CONSTRAINT event_feeling_before_id_fkey FOREIGN KEY (feeling_before_id)
                        REFERENCES actual_feeling (id),
                        CONSTRAINT event_feeling_after_id_fkey FOREIGN KEY (feeling_after_id)
                        REFERENCES actual_feeling (id)
                    );
                    CREATE TABLE tag (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        color_id SMALLINT,
                        name VARCHAR(20),
                        CONSTRAINT tag_user_id_fkey FOREIGN KEY (user_id)
                        REFERENCES emotional_user (id),
                        CONSTRAINT tag_color_id_fkey FOREIGN KEY (color_id)
                        REFERENCES color (id)
                    );

                    CREATE TABLE feeling_object_tag (
                        feeling_object_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_feeling_object_id_fkey FOREIGN KEY (feeling_object_id)
                        REFERENCES feeling_object (id),
                        CONSTRAINT feeling_object_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(feeling_object_id, tag_id)
                    );
                    CREATE TABLE actual_feeling_tag (
                        actual_feeling_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_actual_feelingt_id_fkey FOREIGN KEY (actual_feeling_id)
                        REFERENCES actual_feeling (id),
                        CONSTRAINT actual_feeling_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(actual_feeling_id, tag_id)
                    );
                    CREATE TABLE event_tag (
                        event_id INTEGER,
                        tag_id INTEGER,
                        CONSTRAINT tag_event_id_fkey FOREIGN KEY (event_id)
                        REFERENCES event (id),
                        CONSTRAINT event_tag_id_fkey FOREIGN KEY (tag_id)
                        REFERENCES tag (id),
                        PRIMARY KEY(event_id, tag_id)
                    );
                    """,
                    # Create triggers
                    """
                    CREATE OR REPLACE FUNCTION event_stamp() 
                        RETURNS trigger AS $event_stamp$
                            BEGIN
                                -- true ids
                                IF NEW.feeling_before_id = NEW.feeling_after_id THEN
                                    RAISE EXCEPTION 'before feeling can not be after feeling';
                                END IF;

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_before_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_before user';
                                END IF;

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_before_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_before user';
                                END IF;

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_after user';
                                END IF;

                                IF NEW.feeling_before_id IS NOT NULL AND NEW.feeling_after_id IS NOT NULL AND
                                    (SELECT a.user_id 
                                    FROM actual_feeling a 
                                    JOIN actual_feeling b 
                                    ON a.id = NEW.feeling_before_id 
                                    AND b.id = NEW.feeling_after_id
                                    AND a.user_id = b.user_id) IS NULL THEN
                                    RAISE EXCEPTION 'feeling_before user not equal feeling_after user';
                                END IF;

                                -- time before < time after
                                IF NEW.feeling_before_id IS NOT NULL AND NEW.feeling_after_id IS NOT NULL AND
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_before_id) >
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'feeling_before can not be after the feeling_after';
                                END IF;

                                RETURN NEW;
                            END;
                        $event_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER event_stamp_tr BEFORE INSERT OR UPDATE ON event
                        FOR EACH ROW EXECUTE PROCEDURE event_stamp();


                    CREATE OR REPLACE FUNCTION actual_feeling_stamp() 
                        RETURNS trigger AS $actual_feeling_stamp$
                            BEGIN
                                -- true ids
                                IF NEW.user_id != (SELECT a.user_id FROM feeling_object a WHERE a.id = NEW.feeling_object_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_object user';
                                END IF;

                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $actual_feeling_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER actual_feeling_stamp_tr BEFORE INSERT OR UPDATE ON actual_feeling
                        FOR EACH ROW EXECUTE PROCEDURE actual_feeling_stamp();
                    """,
                    # Create procedures
                    """
                    CREATE OR REPLACE FUNCTION get_report(user_name text)
                    RETURNS TABLE (id INTEGER, user_id INTEGER, report_time timestamp) AS $$
                        SELECT a.id, a.user_id, a.time
                        FROM actual_feeling a
                        JOIN emotional_user ON emotional_user.id = a.user_id
                        WHERE emotional_user.name = user_name;
                    $$ LANGUAGE SQL;
                    """,
                    # Insert data
                    '''
                    INSERT INTO color (id, name) 
                    VALUES 	
                        (1, 'red'),
                        (2, 'green'),
                        (3, 'blue'),
                        (4, 'white'),
                        (5, 'black'),
                        (6, 'yellow'),
                        (7, 'orange'),
                        (8, 'purpure');

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

                    INSERT INTO emotional_user (id, name, pass_hash, email, registration_date) 
                    VALUES  
                        (1, 'Aleks', md5('helloworld'), 'manaleksdev@gmail.com', current_timestamp),
                        (2, 'Natasha', md5('helloworld'), '',current_timestamp);

                    INSERT INTO feeling_object (id, user_id, name) 
                    VALUES  
                        (1, 1, 'Work'),
                        (2, 1, 'KSU'),
                        (3, 2, 'Eat'),
                        (4, 2, 'Sport');

                    INSERT INTO actual_feeling (user_id, feeling_id, feeling_object_id, intensity, time)
                    VALUES 
                        (1, 1, 1, 10, current_timestamp),
                        (2, 1, 3, 10, current_timestamp),
                        (1, 3, 2, 10, current_timestamp),
                        (1, 2, 2, 1, current_timestamp);
                            
                    INSERT INTO event (user_id, feeling_before_id, feeling_after_id, name) 
                    VALUES 
                        (1, 1, 4, 'hello'),
                        (1, 1, 3, 'hello'),
                        (1, 1, Null, 'hello'),
                        (1, Null, Null, 'hello');

                    INSERT INTO tag (id, user_id, color_id, name) 
                    VALUES 
                        (1, 1, 1, 'I do now like it'),
                        (2, 2, 4, 'My best day'),
                        (3, 2, 5, 'University'),
                        (4, 1, 2, 'travel');

                    INSERT INTO feeling_object_tag (feeling_object_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (2, 2),
                        (3, 2),
                        (4, 1);

                    INSERT INTO event_tag (event_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (1, 2),
                        (1, 4),
                        (1, 3);
                    '''
]

emot_db = EmotionalDB(emotional_db_writer_config, create_commands)
emot_db.tables_work()

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

# GAME
@app.route('/game', methods=['GET', 'POST'])
def game():
    return render_template('game.html')

@app.route('/gameover', methods=['GET', 'POST'])
def gameover():
    return render_template('gameover.html')


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
            # Write new
            querry =    '''
                            SELECT id
                            FROM feeling
                            WHERE name = '{}'
                        '''.format(feeling)
            feeling_id = emot_db.select(command=querry)

            querry =    '''
                        INSERT INTO actual_feeling (user_id, feeling_id, feeling_object_id, intensity, time)
                        VALUES 
                            (1, {}, 1, 10, current_timestamp)
                        '''.format(feeling_id[0][0])
            emot_db.insert(command=querry)
            
            # Get result
            querry =    '''
                            SELECT * 
                            FROM get_report('{}') 
                        '''.format(user)
            result = emot_db.select(command=querry)
        else: 
            result = []

        return render_template('emotional_index.html', feelings=feelings, data=result)

    return render_template('emotional_index.html', feelings=feelings)

if __name__ == "__main__":
    app.run(debug=True)