# 2022/5/6  22:15  liujiaqi
import numpy as np
import json
from typing import Union, Tuple, Any, Callable, Iterator, Set, Optional, overload, TypeVar, Mapping, Dict, List


class MessageType:
    # server 发送给 client 的消息类型
    # server发送的第一个字节的 ASCII 值 - 33 ('!')
    lobby = 0
    server_active = 1  # server主动发送的消息

    def encode(self, msg):
        pass

    def decode(self, msg):
        pass

    @staticmethod
    def write(msg):
        print(msg)


def myprint(msg):
    print('myprint')
    print(msg)


class A:
    def __init__(self, t: type):
        assert isinstance(t, type)
        self.t = t

    def aa(self):
        raise KeyError("123234235")


if __name__ == '__main__':
    coins = np.array([1,2,3])
    idx = coins > 1
    c = coins[idx]
    print(len(idx), type(idx), idx, c)

    for line in open('cards_2.txt'):
        print(len(line), f"[{line}]")

    for line in open('cards_2.txt'):
        line = line.strip()
        print(len(line), f"[{line}]")




