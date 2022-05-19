# 2022/5/10  21:54  liujiaqi
from utils import actionregister


class Game(actionregister.ActionRegister):
    '''
    raise ValueError 代表指令有误或执行的游戏指令不符合游戏规则，建议重新输入action，进程不应退出
    raise ValueError 前应保持 action 前的状态，即 action 错误不应改变 game 的属性
    '''

    def __init__(self, players, ptype=None):
        super(Game, self).__init__()
        if not isinstance(players, tuple) and not isinstance(players, list):
            raise ValueError("Players should be a tuple or a list.")
        if ptype is not None and not isinstance(ptype, type):
            raise ValueError("Player type is not a class type.")
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
            raise ValueError(f'Warning: game action has no player name.')  # runtimeerror 要退出游戏， ValueError 为action 错误可继续move
        name = info[0]
        if name not in self.players:
            raise ValueError(f'Player [{name}] is not in this game.')
        p = self.players[name]
        info = tuple(info[1:])
        ins, args = self.parse_action(info)
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

    def show(self):
        raise NotImplementedError


if __name__ == '__main__':
    pass
