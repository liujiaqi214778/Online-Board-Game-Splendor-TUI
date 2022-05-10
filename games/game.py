# 2022/5/10  21:54  liujiaqi


class Game:

    MaxN = 4
    MinN = 2

    def __init__(self, players):  # *** 增加输出玩家tmpcards信息, 牌库卡剩余信息
        self.actions = {}

    def register_actions(self, item, method):
        if not isinstance(method, type(self.__init__)):
            print('error')
        else:
            print('True')
        self.actions[item] = method

    def move(self, action: str):
        raise NotImplementedError

    def quit(self, player):
        raise NotImplementedError

    def is_end(self):
        raise NotImplementedError

    def _set_end(self, current_player):
        raise NotImplementedError

    def win_msg(self):
        raise NotImplementedError

    def get_players(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def update_board(self, info):
        raise NotImplementedError

    def info_on_board(self):
        raise NotImplementedError

    def all_actions(self):  # 返回所有actions
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def judge(self):
        pass


if __name__ == '__main__':
    a = Game(1)
    b = a.register_actions
    print(type(a.__init__))
    print(isinstance(b, type(b)))
    a.register_actions('a', a.show)
