# 2022/5/6  14:46  liujiaqi
import queue
from threading import Thread


class Event(Thread):
    def __init__(self):
        super(Event, self).__init__(daemon=False)
        self.q = queue.Queue()
        self._end = True

    def run(self) -> None:
        self._end = False
        while not self._end:
            v = input()
            v = v.strip()
            if len(v) != 0:
                self.q.put(v)

    def end(self):
        self._end = True

    def get(self):
        assert not self.q.empty() or self.is_alive()
        try:
            out = self.q.get_nowait()
        except:
            return None
        return out


event = Event()


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

