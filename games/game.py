# 2022/5/10  21:54  liujiaqi
from utils import actionregister
import random


class Game(actionregister.ActionRegister):
    '''
    raise Warning 代表指令有误或执行的游戏指令不符合游戏规则，建议重新输入action，进程不应退出
    raise Warning 前应保持 action 前的状态，即 action 错误不应改变 game 的属性
    '''

    def __init__(self, players, ptype=None, shuffle=False):
        super(Game, self).__init__()
        if not isinstance(players, tuple) and not isinstance(players, list):
            raise TypeError("Players should be a tuple or a list.")
        if ptype is not None and not isinstance(ptype, type):
            raise TypeError("Player type is not a class type.")
        '''if len(players) == 0:
            raise ValueError(f"class {type(self).__name__}: No player.")'''
        if shuffle:
            players = list(players)
            random.shuffle(players)
        self.players = {}
        for p in players:
            if ptype is not None:
                self.players[p] = ptype(p)
            else:
                self.players[p] = p

    @classmethod
    def max_player_n(cls):
        raise NotImplementedError

    @classmethod
    def min_player_n(cls):
        raise NotImplementedError

    def __call__(self, action):
        self.move(action)

    def move(self, action: str):
        # action: name ins args
        if self.is_end():
            return
        info = action.split()
        if len(info) < 2:
            raise Warning(f'Warning: game action has no player name.')
        name = info[0]
        if name not in self.players:
            raise Warning(f'Player [{name}] is not in this game.')

        info[0] = info[1]
        info[1] = self.players[name]
        # key playerobj args

        super(Game, self).__call__(info)

        self._set_end(name)

    def quit(self, player):
        self.players.pop(player, None)

    def is_end(self):
        raise NotImplementedError

    def _set_end(self, current_player):
        raise NotImplementedError

    def win_info(self) -> str:
        raise NotImplementedError

    def get_players(self):
        return tuple(self.players.keys())

    def next_player(self):
        if '_pgen' not in self.__dict__:
            self._pgen = self._nextp_generator()  # 生成器
        return next(self._pgen)  # 这里得到的是下面 yield 出来的 n

    def _nextp_generator(self):
        while True:
            # 遍历dict时如果有其他线程添加/删除元素则会 RuntimeError, 转换成tuple避免此问题
            for n in tuple(self.players.keys()):
                yield n  # 函数执行中断，保存协程上下文并返回n

    def load(self):
        raise NotImplementedError

    def set_state(self, state):
        raise NotImplementedError

    def state(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError


if __name__ == '__main__':
    pass
