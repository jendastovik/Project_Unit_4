import sqlite3
from passlib.hash import sha256_crypt

hasher = sha256_crypt.using(rounds=30000)
def make_hash(password):
    return hasher.hash(password)

def check_hash(password, hash):
    return hasher.verify(password, hash)

class DatabaseWorker:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
    def run_query(self, query:str):
        self.cursor.execute(query)
        self.conn.commit()

    def insert(self, query, params=None):
        if params is None:
            self.cursor.execute(query)
            self.conn.commit()
        else:
            self.cursor.execute(query, params)
    
    def search(self, query, multiple=False):
        result = self.cursor.execute(query)
        if multiple:
            return result.fetchall() # returns multiple valuses in a list
        else:
            return result.fetchone() # returns a singele value
    
    def create(self):
        query = """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password VARCHAR(256) NOT NULL,
            username TEXT NOT NULL
            )"""
        self.run_query(query)

    def create_custom_table(self, atr: dict, table_name: str):
        """
        atr: dictionary with the attributes of the table and their types
        table_name: name of the table
        """
        atrs = ""
        for a in atr:
            atrs += f"{a} {atr[a]},"
        atrs = atrs[:-1]
        query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            {atrs}
            )"""
        self.run_query(query)

    def close(self):
        self.conn.close()

