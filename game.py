# 2022/5/2  20:03  liujiaqi

from sockutils import *
from board import Board, Player


class Game:
    def __init__(self, sock, name, tid):
        self.socket = sock
        self.name = name
        self.tid = tid
        self.gettableinfo()
        self.board = Board()

    def gettableinfo(self):
        # tid -> playerlist,
        pass

    def move(self):
        pass
