# 2022/5/10  21:54  liujiaqi


class Game:

    MaxN = 4
    MinN = 2

    def __init__(self, players):  # *** 增加输出玩家tmpcards信息, 牌库卡剩余信息
        pass

    def move(self, action: str):
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
