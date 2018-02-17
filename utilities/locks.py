import threading


class Lock:
    multithreaded = False

    def __init__(self):
        self.lock = threading.Lock()

    def __enter__(self):
        if Lock.multithreaded:
            self.lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        if Lock.multithreaded:
            self.lock.release()
