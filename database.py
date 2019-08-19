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
            create table if not exists Scan (
                time real,
                host text,
                port integer
            );
        ''')
        cursor.execute('''
            create table if not exists Header (
                scan_id integer,
                line text
            );
        ''')
        cursor.execute('create index if not exists idxLine on Header (line)')
        cursor.execute('create index if not exists idxScan on Header (scan_id)')
        db.commit()
        self._db = db

    def insert(self, host, port, lines):
        now = time.time()
        cursor = self._db.cursor()
        cursor.execute('''
            insert into Scan (time, host, port) values (?, ?, ?)
        ''', (now, host, port))
        scan_id = cursor.lastrowid
        values = []
        for line in lines:
            values.append((scan_id, line))
        cursor.executemany('''
            insert into Header (scan_id, line) values (?, ?)
        ''', values)
        self._db.commit()

    def search(self, query):
        cursor = self._db.cursor()
        cursor.execute('''
            select Header.scan_id, Scan.host, Scan.port
            from Header
            join Scan on Scan.rowid = Header.scan_id
            where line regexp ?
            group by Header.scan_id
        ''', (query,))
        results = []
        for row in cursor:
            scan_id = row[0]
            host = row[1]
            port = row[2]
            results.append((host, port, self.__get_lines(scan_id)))
        return results

    def __get_lines(self, scan_id):
        cursor = self._db.cursor()
        cursor.execute('''
            select line
            from Header
            where scan_id = ?
            order by rowid
        ''', (scan_id,))
        return [x[0] for x in cursor]

def regexp(expr, text):
    try:
        reg = re.compile(expr)
        if reg.search(text) is not None:
            return True
    except:
        pass
    return False
