# 2022/5/10  21:54  liujiaqi
from collections import Iterable


class Game:

    # MaxN = 4
    # MinN = 2

    def __init__(self, players, ptype=None):  # *** 增加输出玩家tmpcards信息, 牌库卡剩余信息
        if not isinstance(players, Iterable):
            raise ValueError("Players should be a iterable.")
        if ptype is not None and not isinstance(ptype, type):
            raise ValueError("Player type is not a class type.")
        self.players = {}
        for p in players:
            if ptype is not None:
                self.players[p] = ptype(p)
            else:
                self.players[p] = p
        self.actions = {}

    @classmethod
    def max_player_n(cls):
        raise NotImplementedError

    @classmethod
    def min_player_n(cls):
        raise NotImplementedError

    def register_action(self, item, method):
        if not isinstance(method, type(self.__init__)):
            raise ValueError(f"Value Type [{type(method)}] is not a class method")
        if isinstance(item, Iterable):
            for i in item:
                self.actions[i] = method
        else:
            self.actions[item] = method

    def move(self, action: str):
        # action: name ins args
        if self.is_end():
            return
        info = action.split()
        if len(info) < 2:
            raise ValueError(f'Warning: action empty.')  # runtimeerror 要退出游戏， ValueError 为action 错误可继续move
        name = info[0]
        if name not in self.players:
            raise ValueError(f'Player [{name}] is not in this game.')
        p = self.players[name]
        ins = info[1]
        args = tuple(info[2:])
        if ins not in self.actions:
            raise ValueError(f'Warning: action [{ins}] is not exist.')

        self.actions[ins](p, *args)
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

    def load(self):
        raise NotImplementedError

    def update_board(self, info):
        raise NotImplementedError

    def info_on_board(self):
        raise NotImplementedError

    def all_actions(self) -> str:  # 返回所有actions的说明
        raise NotImplementedError

    def show(self):
        raise NotImplementedError


if __name__ == '__main__':
    a = Game(1)
    b = a.register_action
    print(type(a.__init__))
    print(isinstance(b, type(b)))
    a.register_action('a', a.show)
