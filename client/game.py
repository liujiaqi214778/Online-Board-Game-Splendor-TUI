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
        print('start game....')
        # time.sleep(3)
        t = 1 / self.fps
        while True:
            if isDead():
                return
            time.sleep(t)
            info = event.event.get()  # event线程接收标准输入的指令
            if info:
                write(self.socket, 'game ' + info)
                if info.startswith('quit'):
                    print('Quit the game...')
                    return

            msg = active_msg_reciever.read()
            if msg is None:
                continue

            if msg.startswith('board'):
                try:
                    self.game.update_board(msg[5:])
                except:
                    print(f'update_board error, json:\n {msg[5:]}')
                    return
                self.game.show()
            elif msg.startswith('action'):
                print("It's your turn. Action or help.")
                continue
            elif msg.startswith('gend'):
                print(msg[4:].strip())
                return
            else:
                # print('Unknown msg:')
                print(msg)
