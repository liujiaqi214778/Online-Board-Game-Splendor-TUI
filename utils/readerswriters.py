# 2022/5/19  12:18  liujiaqi
from threading import Semaphore
import functools


class ReadersWriters:
    # 读写公平的读者写者问题
    def __init__(self):
        self.rcount = 0
        self.fair_mutex = Semaphore(1)  # 读写公平锁. Semaphore(1) 等效于lock
        self.wmutex = Semaphore(1)  # 写锁
        self.cmutex = Semaphore(1)  # 写rcount的锁
        # https://docs.python.org/3/library/threading.html

    @staticmethod
    def reader(method):
        @functools.wraps(method)  # 保留被装饰函数的属性, 比如method.__name__
        def wrapped(rself: ReadersWriters, *args, **kwargs):

            class ReaderContext:
                def __enter__(self):
                    with rself.fair_mutex, rself.cmutex:  # with 上下文管理，两个mutex依次acquire，退出时反过来release
                        if rself.rcount == 0:
                            rself.wmutex.acquire()
                        rself.rcount += 1

                def __exit__(self, exc_type, exc_val, exc_tb):
                    with rself.cmutex:
                        rself.rcount -= 1
                        if rself.rcount == 0:
                            rself.wmutex.release()

            with ReaderContext():  # with会确保__exit__后再抛出异常
                return method(rself, *args, **kwargs)
        return wrapped

    @staticmethod
    def writer(method):
        @functools.wraps(method)
        def wrapped(self: ReadersWriters, *args, **kwargs):
            with self.fair_mutex, self.wmutex:
                return method(self, *args, **kwargs)

        return wrapped
