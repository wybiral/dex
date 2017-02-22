import re
import sqlite3
import time

def get_database():
    return SqliteDb()


class Database:

    def insert(self, host, lines):
        raise NotImplementedError

    def search(self, query):
        raise NotImplementedError


class SqliteDb(Database):

    def __init__(self, filename='database.db'):
        db = sqlite3.connect(filename)
        db.create_function('REGEXP', 2, regexp)
        cursor = db.cursor()
        cursor.execute('''
            create table if not exists Header (
                time real,
                host text,
                line text
            )
        ''')
        cursor.execute('create index if not exists idxHost on Header (host)')
        cursor.execute('create index if not exists idxLine on Header (line)')
        db.commit()
        self._db = db

    def insert(self, host, lines):
        now = time.time()
        cursor = self._db.cursor()
        values = []
        for line in lines:
            values.append((now, host, line))
        cursor.executemany('''
            insert into Header (time, host, line) values (?, ?, ?)
        ''', values)
        self._db.commit()

    def search(self, query):
        cursor = self._db.cursor()
        cursor.execute('''
            select distinct host from Header where line regexp ?
        ''', (query,))
        results = []
        for row in cursor:
            host = row[0]
            results.append((host, self.__get_lines(host)))
        return results

    def __get_lines(self, host):
        cursor = self._db.cursor()
        cursor.execute('''
            select line from Header where host = ? order by line
        ''', (host,))
        return [x[0] for x in cursor]

def regexp(expr, text):
    try:
        reg = re.compile(expr)
        if reg.search(text) is not None:
            return True
    except:
        pass
    return False
