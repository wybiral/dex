try:
    from http.client import HTTPResponse, HTTPConnection
except:
    from httplib import HTTPResponse, HTTPConnection
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from random import randrange as rand
from threading import Thread, active_count
from time import sleep
from database import get_database


class Scanner:

    def __init__(self, threadcount=500):
        self.threadcount = threadcount

    def run(self):
        queue = Queue()
        for i in range(self.threadcount):
            self._start_thread(self._worker, queue)
        self._start_thread(self._collect, queue)

    def block(self):
        while active_count() > 0:
            sleep(0.5)

    def _start_thread(self, fn, queue):
        thread = Thread(target=fn, args=(queue,))
        thread.daemon = True
        thread.start()

    def _collect(self, queue):
        db = get_database()
        while True:
            host, lines = queue.get()
            if lines:
                db.insert(host, lines)

    def _worker(self, queue):
        while True:
            try:
                queue.put(self._work())
            except KeyboardInterrupt as e:
                raise e
            except:
                continue

    def _work(self):
        host = '%s.%s.%s.%s' % (rand(256), rand(256), rand(256), rand(256))
        con = HTTPConnection(host, 80, timeout=1.0)
        con.request('GET', '/')
        res = con.getresponse()
        headers = res.getheaders()
        lines = []
        for key, value in headers:
            if len(key) < 256 and len(value) < 256:
                lines.append('{}: {}'.format(key, value))
        return (host, lines)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.run()
    try:
        scanner.block()
    except KeyboardInterrupt:
        pass
