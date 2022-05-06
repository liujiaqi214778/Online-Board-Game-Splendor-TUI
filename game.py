# 2022/5/2  20:03  liujiaqi

from sockutils import *
from board import Board, Player
import event


class Game:
    def __init__(self, sock, name):
        self.socket = sock
        self.name = name
        # self.tid = tid
        self.gettableinfo()
        self.board = Board()

    def gettableinfo(self):
        # tid -> playerlist,
        pass

    def move(self):
        pass
