try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from random import randrange as rand
from socket import socket, AF_INET, SOCK_STREAM
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
            sleep(10)

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
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(1.0)
        s.connect((host, 80))
        s.send(b'GET / HTTP/1.0\r\n\r\n')
        buf = s.recv(1024 * 2)
        parts = buf.split(b'\r\n\r\n', 1)
        if len(parts) > 1:
            raw = parts[0]
            lines = parts[0].split(b'\r\n')
            lines = [x.decode('utf-8', 'ignore') for x in lines]
        else:
            lines = []
        return (host, lines)


if __name__ == '__main__':
    scanner = Scanner()
    scanner.run()
    try:
        scanner.block()
    except KeyboardInterrupt:
        pass
