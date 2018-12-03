import hashlib

class Blockchain(object):
    """docstring"""

    def __init__(self, emot_db):
        """Constructor"""
        self.emot_db = emot_db

    def write_block(self, name, amount, to_whom, hash=''):
        Blocks = self.emot_db.select('''SELECT * FROM Block''')
        print(Blocks[-1][4].encode())
        hash = hashlib.md5(str(Blocks[-1]).encode()).hexdigest()
        before_id = Blocks[-1][0]
        self.emot_db.insert('''INSERT INTO Block (id, creditor, recipient, amount, hash, before_id) 
                            VALUES ({}, '{}', '{}', '{}',
                            '{}', {});'''.format(before_id+1, name, amount, to_whom, hash, before_id))
        self.emot_db.insert('''
                            DROP TABLE IF EXISTS color;
                            CREATE TABLE color (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(20),
                            code VARCHAR(10)
                            );''')


    def check_integrity(self):
        results = []
        Blocks = self.emot_db.select('''SELECT * FROM Block''')
        for i in range(len(Blocks)):
            if i == len(Blocks)-1:
                results.append(('LAST BLOCK', Blocks[i]))
                break

            calculated_hash = hashlib.md5(str(Blocks[i]).encode()).hexdigest()
            written_hash = Blocks[i+1][4]
            if calculated_hash == written_hash:
                results.append(('OK', Blocks[i]))
            else:
                results.append(('CORRUPTED', Blocks[i]))

        return results
