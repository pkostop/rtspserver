import threading


class AtomicCounter:
    def __init__(self, initial_value=0):
        self.counter = initial_value
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.counter += 1
            return self.counter
