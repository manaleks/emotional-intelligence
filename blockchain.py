import hashlib

import db
import db_config

db_params = db_config.emotional_db_writer_config

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

tables_delete_tables = [
                        """
                        DROP TABLE block
                        """
                        ]

db.tables_work(db_params, tables_delete_tables)
db.tables_work(db_params, tables_create_commands)
db.insert(db_params,'''INSERT INTO Block (id, creditor, recipient, amount, hash) 
                       VALUES (1, 'GENESIS BLOCK C', 'GENESIS BLOCK R', 'GENESIS BLOCK A', 'GENESIS BLOCK HASH');''')


def write_block(name, amount, to_whom, hash=''):
    Blocks = db.select(db_params, '''SELECT * FROM Block''')
    print(Blocks[-1][4].encode())
    hash = hashlib.md5(str(Blocks[-1]).encode()).hexdigest()
    before_id = Blocks[-1][0]
    db.insert(db_params,'''INSERT INTO Block (id, creditor, recipient, amount, hash, before_id) 
                           VALUES ({}, '{}', '{}', '{}',
                           '{}', {});'''.format(before_id+1, name, amount, to_whom, hash, before_id))


def check_integrity():
    results = []
    Blocks = db.select(db_params, '''SELECT * FROM Block''')
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

def main():
    check_integrity()
    write_block(name="masha", amount="100", to_whom="perto")
    write_block(name="masha", amount="100", to_whom="perto")

"""
if __name__ == '__main__':
    main()
    Blocks = db.select(db_params, '''SELECT * FROM Block''')
    print(Blocks)
"""
