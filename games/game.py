# 2022/5/10  21:54  liujiaqi


class Game:

    MaxN = 4
    MinN = 2

    def __init__(self, players):  # *** 增加输出玩家tmpcards信息, 牌库卡剩余信息
        pass

    def move(self, action: str):  # return > 0 游戏结束 return -1: 错误的action, return < -1 其他错误
        raise NotImplementedError

    def win_msg(self):
        raise NotImplementedError

    def get_players(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def update_board(self, info):  # 更新on board的信息，给client 打印
        raise NotImplementedError

    def info_on_board(self):
        raise NotImplementedError

    def all_actions(self):  # 返回所有actions
        raise NotImplementedError

    def show(self):
        raise NotImplementedError
