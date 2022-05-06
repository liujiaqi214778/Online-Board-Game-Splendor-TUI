# 2022/5/6  14:46  liujiaqi
import queue
from threading import Thread


class Event(Thread):
    def __init__(self):
        super(Event, self).__init__(daemon=False)
        self.q = queue.Queue()

    def run(self) -> None:
        while True:
            v = input()
            v = v.strip()
            if len(v) != 0:
                self.q.put(v)

    def get(self):
        try:
            out = self.q.get_nowait()
        except:
            return None
        return out


if __name__ == '__main__':
    from board import ClearCLI
    import time

    e = Event()
    e.is_alive()
    e.isDaemon()

    e.start()

    while True:
        fps = 10
        time.sleep(1/fps)
        msg = e.get()
        if msg is not None:
            print(msg)

