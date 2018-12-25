# -*- coding: utf8 -*-
import os
from flask import Flask, request, render_template

from blockchain import Blockchain
from dbhelper import dbhelper
import emotional

try:
    import config
    db_config = config.emotional_db_config
except ModuleNotFoundError:
    db_config = {
                "DBHOST":os.environ['DBHOST'],
                "DBUSER":os.environ['DBUSER'],
                "DBNAME":os.environ['DBNAME'],
                "DBPASS":os.environ['DBPASS']
                }

emot_db = dbhelper(db_config, emotional.create_commands)
emot_db.tables_work()

B_chain = Blockchain(emot_db)


app = Flask(__name__)

# MAIN
def main_page():
    return render_template('main.html')
def simple_text(num):
    return "Hello!" + str(num)

rules = []
rules.append({"rule":'/',"name":"main_page","method":main_page})
rules.append({"rule":'/simple_text/<num>',"name":"simple_text","method":simple_text})
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
def blockchain():
    if request.method == 'POST':
        lender = request.form['lender']
        amount = request.form['amount']
        borrower = request.form['borrower']

        B_chain.write_block(name=lender, amount=amount, to_whom=borrower, hash='')
    return render_template('blockchain.html')

@app.route('/blockchain/checking', methods=['GET'])
def blockchain_check():
    results = B_chain.check_integrity()
    return render_template('blockchain.html', results=results)



# EMOTIONAL
feelings = ['joy','trust', 'anger','anticipation','disgust','sadness','surprise','fear']
@app.route('/emotional', methods=['GET', 'POST'])
def emotional_page():
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
                            FROM get_group_feelings('{}', '{}', md5('{}'))
                        '''.format('15-ИСбо-2(б)', user,'helloworld')
            result = emot_db.select(command=querry)
            print(result)
        else: 
            result = []

        return render_template('emotional.html', feelings=feelings, data=result)

    return render_template('emotional.html', feelings=feelings)

if __name__ == "__main__":
    app.run(debug=True)