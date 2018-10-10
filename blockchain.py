import json
import hashlib

blocks = [b'GENESIS BLOCK']

tables_create_commands = (
        """
        CREATE TABLE block (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """ CREATE TABLE parts (
                part_id SERIAL PRIMARY KEY,
                part_name VARCHAR(255) NOT NULL
                )
        """,
        """
        CREATE TABLE part_drawings (
                part_id INTEGER PRIMARY KEY,
                file_extension VARCHAR(5) NOT NULL,
                drawing_data BYTEA NOT NULL,
                FOREIGN KEY (part_id)
                REFERENCES parts (part_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE vendor_parts (
                vendor_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                PRIMARY KEY (vendor_id , part_id),
                FOREIGN KEY (vendor_id)
                    REFERENCES vendors (vendor_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (part_id)
                    REFERENCES parts (part_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
        )
        """)
tables_delete_tables = (
        """
        DROP TABLE vendor_parts
        """,
        """
        DROP TABLE part_drawings
        """,
        """
        DROP TABLE parts
        """,
        """
        DROP TABLE vendors
        """
)


def write_block(name, amount, to_whom, hash=''):
    hash = hashlib.md5(blocks[-1]).hexdigest()
    data = {
        'name':name,
        'amount':amount,
        'to_whom':to_whom,
        'hash':hash,
    }
    blocks.append(json.dumps(data).encode())

def check_integrity():
    results = []
    for i in range(len(blocks)):
        if i == len(blocks)-1:
            results.append(('LAST BLOCK', blocks[i]))
            break

        calculated_hash = hashlib.md5(blocks[i]).hexdigest()
        written_hash = json.loads(blocks[i+1])["hash"]
        if calculated_hash == written_hash:
            results.append(('OK', blocks[i]))
        else:
            results.append(('CORRUPTED', blocks[i]))

    return results

def main():
    check_integrity()
    write_block(name="masha", amount="100", to_whom="perto")

if __name__ == '__main__':
    main()