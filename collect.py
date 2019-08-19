'''
Requires ipv4scan: https://github.com/wybiral/ipv4scan

To use you'll need to pipe the scan results from ipv4scan into this script:
    ipv4scan -n 500 | python3 collect.py

This script will read the output from stdin and copy them into the dex sqlite3
database to show up in search results.
'''

from json import loads
from sys import stdin
from database import get_database

db = get_database()

for line in stdin:
    x = loads(line)
    host = x['ip']
    port = x['port']
    lines = x['headers'].split('\r\n')
    print('{}:{}'.format(host, port))
    db.insert(host, port, lines)
