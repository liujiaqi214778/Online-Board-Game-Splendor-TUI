# 2022/5/17  22:29  liujiaqi
import time
from utils import event
from utils.actionregister import ActionRegister
from games.board import Board
from .sockutils import isDead, write, active_msg_reciever


class Game(ActionRegister):
    def __init__(self, sock, gname, fps=30):
        self.socket = sock
        self.game_name = gname
        self.game = Board([])  # 改成根据gname找到游戏类型
        self.fps = fps
        self.register_action()

    def start(self):
        pass
