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
"""
os.environ['DBHOST'] = "localhost"
os.environ['DBUSER'] = "emotional_manager"
os.environ['DBNAME'] = "emotional_db"
os.environ['DBPASS'] = "emotionalpass"
"""

emotional_db_writer_config = {
                            "DBHOST":os.environ['DBHOST'],
                            "DBUSER":os.environ['DBUSER'],
                            "DBNAME":os.environ['DBNAME'],
                            "DBPASS":os.environ['DBPASS']
                            }

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
'''

create_commands = [
                    # DROP tables, functions and triggers
                    """
                    DROP TRIGGER IF EXISTS event_stamp_tr ON event;
                    DROP TRIGGER IF EXISTS actual_feeling_stamp_tr ON actual_feeling;
                    DROP TRIGGER IF EXISTS actual_feeling_tag_stamp_tr ON actual_feeling_tag;
                    DROP TRIGGER IF EXISTS feeling_object_tag_stamp_tr ON feeling_object_tag;
                    DROP TRIGGER IF EXISTS event_tag_stamp_tr ON event_tag;
                    DROP FUNCTION IF EXISTS event_stamp();


                    DROP FUNCTION IF EXISTS get_actual_feelings(user_name text, pass_hash text);
                    DROP FUNCTION IF EXISTS get_events(user_name text, pass_hash text);

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
                    -- event insert
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

                                IF NEW.user_id != (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'user not equal feeling_after user';
                                END IF;

                                -- time before < time after
                                IF NEW.feeling_before_id IS NOT NULL AND NEW.feeling_after_id IS NOT NULL AND
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_before_id) >
                                    (SELECT time FROM actual_feeling WHERE actual_feeling.id = NEW.feeling_after_id) THEN
                                    RAISE EXCEPTION 'feeling_before can not be after the feeling_after';
                                END IF;

                                -- set time
                                IF NEW.time IS NULL THEN
                                    NEW.time = current_timestamp;
                                END IF;

                                RETURN NEW;
                            END;
                        $event_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER event_stamp_tr BEFORE INSERT OR UPDATE ON event
                        FOR EACH ROW EXECUTE PROCEDURE event_stamp();

                    -- actual_feeling insert
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


                    -- feeling_object_tag insert
                    CREATE OR REPLACE FUNCTION feeling_object_tag_stamp() 
                        RETURNS trigger AS $feeling_object_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM feeling_object a WHERE a.id = NEW.feeling_object_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'feeling_object and tag have different owner % %', NEW.feeling_object_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $feeling_object_tag_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER feeling_object_tag_stamp_tr BEFORE INSERT OR UPDATE ON feeling_object_tag
                        FOR EACH ROW EXECUTE PROCEDURE feeling_object_tag_stamp();

                    -- actual_feeling_tag insert
                    CREATE OR REPLACE FUNCTION actual_feeling_tag_stamp() 
                        RETURNS trigger AS $actual_feeling_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM actual_feeling a WHERE a.id = NEW.actual_feeling_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'actual_feeling and tag have different owner % %', NEW.actual_feeling_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $actual_feeling_tag_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER actual_feeling_tag_stamp_tr BEFORE INSERT OR UPDATE ON actual_feeling_tag
                        FOR EACH ROW EXECUTE PROCEDURE actual_feeling_tag_stamp();

                    -- event_tag insert
                    CREATE OR REPLACE FUNCTION event_tag_stamp() 
                        RETURNS trigger AS $event_tag_stamp$
                            BEGIN
                                -- true ids
                                IF (SELECT a.user_id FROM event a WHERE a.id = NEW.event_id) != (SELECT a.user_id FROM tag a WHERE a.id = NEW.tag_id) THEN
                                    RAISE EXCEPTION 'event and tag have different owner % %', NEW.event_id, NEW.tag_id;
                                END IF;
                                RETURN NEW;
                            END;
                        $event_tag_stamp$ LANGUAGE plpgsql;

                    CREATE TRIGGER event_tag_stamp_tr BEFORE INSERT OR UPDATE ON event_tag
                        FOR EACH ROW EXECUTE PROCEDURE event_tag_stamp();
                    """,
                    # Create functions
                    """
                    -- Get users actual_feelings by name
                    CREATE OR REPLACE FUNCTION get_actual_feelings(user_name text, pass_hash text)
                    RETURNS TABLE (feeling VARCHAR(20), color VARCHAR(10), 
                                    feeling_object VARCHAR(20), intensity INTEGER,
                                    report_time timestamp) AS $$
                        SELECT 
                            f.name feeling,
                            c.code color, 
                            fo.name feeling_object, 
                            af.intensity,
                            af.time
                        FROM actual_feeling af
                        JOIN emotional_user eu ON eu.id = af.user_id
                        LEFT JOIN feeling_object fo ON fo.id = af.feeling_object_id
                        LEFT JOIN feeling f ON f.id = af.feeling_id
                        LEFT JOIN color c ON c.id = f.color_id
                        WHERE 1=1
                            AND eu.name = user_name
                            AND eu.pass_hash = pass_hash;
                    $$ LANGUAGE SQL;

                    -- Get users events by name
                    CREATE OR REPLACE FUNCTION get_events(user_name text, pass_hash text)
                    RETURNS TABLE (
                                    event_name VARCHAR(100),
                                    descriprion VARCHAR(255),
                                    event_time timestamp,
                                    place VARCHAR(100),
                                    after_feeling VARCHAR(20), after_color VARCHAR(10), 
                                    after_feeling_object VARCHAR(20), after_intensity INTEGER,
                                    after_time timestamp,
                                    before_feeling VARCHAR(20), before_color VARCHAR(10), 
                                    before_feeling_object VARCHAR(20), before_intensity INTEGER,
                                    before_time timestamp) AS $$
                        SELECT 
                            e.name event_name,
                            e.description description,
                            e.time event_time,
                            e.place,

                            f1.name before_feeling,
                            c1.code before_color, 
                            fo1.name before_feeling_object, 
                            af1.intensity before_intensity,
                            af1.time before_time,

                            f2.name after_feeling,
                            c2.code after_color, 
                            fo2.name after_feeling_object, 
                            af2.intensity after_intensity,
                            af2.time after_time
                        FROM event e
                        JOIN emotional_user eu ON eu.id = e.user_id
                        LEFT JOIN actual_feeling af1 ON af1.id = e.feeling_before_id
                            LEFT JOIN feeling_object fo1 ON fo1.id = af1.feeling_object_id
                            LEFT JOIN feeling f1 ON f1.id = af1.feeling_id
                            LEFT JOIN color c1 ON c1.id = f1.color_id
                        LEFT JOIN actual_feeling af2 ON af2.id = e.feeling_after_id
                            LEFT JOIN feeling_object fo2 ON fo2.id = af2.feeling_object_id
                            LEFT JOIN feeling f2 ON f2.id = af2.feeling_id
                            LEFT JOIN color c2 ON c2.id = f2.color_id
                        WHERE 1=1
                            AND eu.name = user_name
                            AND eu.pass_hash = pass_hash;
                    $$ LANGUAGE SQL;
                    """,
                    # Insert data
                    '''
                    INSERT INTO color (name) 
                    VALUES 	
                        ('red'),
                        ('green'),
                        ('blue'),
                        ('white'),
                        ('black'),
                        ('yellow'),
                        ('orange'),
                        ('purpure');

                    INSERT INTO feeling (name, color_id) 
                    VALUES 	
                        ('joy', 6),
                        ('trust', 2),
                        ('anger', 1),
                        ('anticipation', 4),
                        ('disgust', 8),
                        ('sadness', 3),
                        ('surprise', 7),
                        ('fear', 5);

                    INSERT INTO emotional_user (id, name, pass_hash, email, registration_date) 
                    VALUES  
                        (1, 'Aleks', md5('helloworld'), 'manaleksdev@gmail.com', current_timestamp),
                        (2, 'Natasha', md5('helloworld'), '',current_timestamp);

                    INSERT INTO feeling_object (user_id, name) 
                    VALUES  
                        (1, 'Work'),
                        (1, 'KSU'),
                        (2, 'Eat'),
                        (2, 'Sport');

                    INSERT INTO actual_feeling (user_id, feeling_id, feeling_object_id, intensity, time)
                    VALUES 
                        (1, 1, 1, 10, current_timestamp),
                        (2, 1, 3, 10, current_timestamp),
                        (1, 3, 2, 10, current_timestamp),
                        (1, 2, 2, 1, current_timestamp);
                            
                    INSERT INTO event (user_id, feeling_before_id, feeling_after_id, name, description, place) 
                    VALUES 
                        (1, 1, 3, 'first kiss', 'i remember, it was beautiful', 'girlfriend home'),
                        (1, 3, 4, 'fight', 'run, forest, run', 'outside'),
                        (1, 1, Null, 'exam', 'i sleep too much', 'home'),
                        (1, Null, Null, 'test event', '' , ''),
                        (2, Null, Null, 'hello', '', '');

                    INSERT INTO tag (user_id, color_id, name) 
                    VALUES 
                        (1, 1, 'I do now like it'),
                        (1, 4, 'My best day'),
                        (2, 5, 'University'),
                        (2, 2, 'travel'),
                        (1, 2, 'money');

                    INSERT INTO feeling_object_tag (feeling_object_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (2, 1),
                        (3, 4),
                        (4, 3);

                    INSERT INTO actual_feeling_tag (actual_feeling_id, tag_id) 
                    VALUES 
                        (2, 3),
                        (2, 4),
                        (1, 1),
                        (4, 1);

                    INSERT INTO event_tag (event_id, tag_id) 
                    VALUES 
                        (1, 1),
                        (1, 2),
                        (4, 5),
                        (3, 5);
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
                            FROM get_events('{}', md5('{}')) 
                        '''.format(user,'helloworld')
            result = emot_db.select(command=querry)
        else: 
            result = []

        return render_template('emotional_index.html', feelings=feelings, data=result)

    return render_template('emotional_index.html', feelings=feelings)

if __name__ == "__main__":
    app.run(debug=True)