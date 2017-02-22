try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from random import randrange as rand
try:
    from requests import get
except ImportError:
    print('requests module required:\npip install requests')
    exit()
from threading import Thread, active_count
from time import sleep
from database import get_database


class Scanner:

    def __init__(self, threadcount=100):
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
        host = '.'.join(str(rand(256)) for i in range(4))
        req = get('http://' + host, timeout=1)
        lines = []
        for key, value in req.headers.items():
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
