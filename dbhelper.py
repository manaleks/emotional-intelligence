import psycopg2

class dbhelper(object):
    """docstring"""
    
    def __init__(self, db_params, create_commands):
        """Constructor"""
        self.db_params = db_params
        self.create_commands = create_commands

    def tables_work(self):
        """ create tables in the PostgreSQL database"""
        conn = psycopg2.connect(host=self.db_params["DBHOST"],database=self.db_params["DBNAME"],
                                user=self.db_params["DBUSER"], password=self.db_params["DBPASS"])
        cur = conn.cursor()


        # create table one by one
        for command in self.create_commands:
                cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        """
        try:
            # create table one by one
            for command in commands:
                cur.execute(command)
            # close communication with the PostgreSQL database server
            cur.close()
            # commit the changes
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        """

    def select(self, command):
        conn = psycopg2.connect(host=self.db_params["DBHOST"],database=self.db_params["DBNAME"],
                                user=self.db_params["DBUSER"], password=self.db_params["DBPASS"])
        cur = conn.cursor()
        cur.execute(command)
        data = cur.fetchall()
        #print(data)
        #for row in data:
        #    print(row)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
        return data

    def insert(self, command):
        conn = psycopg2.connect(host=self.db_params["DBHOST"],database=self.db_params["DBNAME"],
                                user=self.db_params["DBUSER"], password=self.db_params["DBPASS"])
        cur = conn.cursor()
        cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
