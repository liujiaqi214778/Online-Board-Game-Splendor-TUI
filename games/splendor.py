import platform
import random
import numpy as np
import json
import os
from games.game import Game
from . import GAME_REGISTRY

from colorama import init
# from enum import Enum

init(autoreset=True)


def json_dumps(*args, **kwargs):
    def default_func(obj):
        if isinstance(obj, np.ndarray):
            return obj.astype(dtype=int).tolist()
        if isinstance(obj, Card) or isinstance(obj, NobleCard):
            return str(obj)
        if isinstance(obj, Player):
            return obj.__dict__
        return obj
    return json.dumps(*args, separators=(',', ':'), default=default_func, **kwargs)
    # return json.dumps(*args, default=default_func, **kwargs)


class Color:  # (Enum):
    White = 0
    Blue = 1
    Green = 2
    Red = 3
    Black = 4
    '''Black = 1
    Red = 2
    Blue = 3
    Green = 4'''
    Yellow = 5

    W = 'W\033[1;30;47m   \033[0m'
    B = 'B\033[40;1m   \033[0m'
    R = 'R\033[41;1m   \033[0m'
    U = 'U\033[44;1m   \033[0m'
    G = 'G\033[42;1m   \033[0m'
    Y = 'Y\033[43;1m   \033[0m'
    Ground_Colors = [W, U, G, R, B, Y]


def container():
    # Yellow 为万能币
    # return np.array([0 for _ in range(len(Color.__members__) - 1)])
    return np.array([0 for _ in range(Color.Yellow)], dtype=np.int32)


class Card:
    def __init__(self, *args):
        # Card('[1,1,1,1,1] 2 1')  costs, color, score
        # Card([1,1,1,1,1], 2, 1)
        # Card('[1,1,1,1,1]', 2, 1)
        # Card(card)
        if len(args) == 1:
            self._init_str(str(args[0]))
            return

        if len(args) != 3:
            raise ValueError(f"Card init Error, args number should be 3. args:[{args}]")

        ct = args[0]
        if isinstance(ct, str):
            ct = json.loads(ct)

        self.costs = np.array(ct, dtype=np.int32)  # numpy array
        if len(self.costs) != Color.Yellow:
            raise ValueError(f"Card init Error, costs format error. [{self.costs}]")
        self.color = args[1]
        self.score = args[2]

    def _init_str(self, ss: str):
        attrs = ss.split()
        if len(attrs) != 3:
            raise ValueError(f"Card init Error [{ss}]")
        costs = json.loads(attrs[0])
        self.costs = np.array(costs, dtype=np.int32) - container()  # 减法为了检查错误
        self.color = int(attrs[1])
        self.score = int(attrs[2])

    def __str__(self):
        return json_dumps(self.costs) + ' ' + str(self.color) + ' ' + str(self.score)


class NobleCard:
    def __init__(self, costs):
        self.score = 3
        if isinstance(costs, str):
            costs = json.loads(costs)
        self.costs = np.array(costs, dtype=np.int32)
        if len(self.costs) != Color.Yellow:
            raise ValueError(f"NobleCard init error, args [{costs}]")

    def __str__(self):
        return json_dumps(self.costs)


class Player:
    def __init__(self, name):
        if isinstance(name, dict):
            try:
                d = name
                self.name = d['name']
                self.coins = np.array(d['coins'], dtype=np.int32)
                self.cards = np.array(d['cards'], dtype=np.int32)
                self.uni_coins = d['uni_coins']
                self.score = d['score']
                self.tmpcards = d['tmpcards']
                for i, v in enumerate(self.tmpcards):
                    self.tmpcards[i] = Card(v)
                return
            except:
                raise ValueError(f"Format parameters error. Player({name}])")
        self.name = name
        self.coins = container()
        self.cards = container()
        # self.vals = container()
        self.uni_coins = 0
        self.score = 0
        self.tmpcards = []

    def __str__(self):  # -> json string
        '''
        # 弃用，json_dumps(self) 效果是一样的
        d = copy.deepcopy(self.__dict__)
        d['coins'] = d['coins'].astype(dtype=int).tolist()
        d['cards'] = d['cards'].astype(dtype=int).tolist()
        tcards = d['tmpcards']
        for i, card in enumerate(tcards):
            tcards[i] = str(card)
        return json.dumps(d, separators=(',', ':'))
        '''
        return json_dumps(self)

    '''def redeem(self, idx):
        if idx >= len(self.tmpcards) or idx < 0:
            print('')
            return -1
        ret = self.buy(self.tmpcards[idx])
        if not ret < 0:
            self.tmpcards.pop(idx)
        return ret'''

    def take_coins(self, coins):
        if sum(self.coins) + sum(coins) > 10:
            raise Warning(f'Your coins should <= 10. [{self.coins}] take[{coins}]')
        self.coins += coins
        # self.vals += coins
        # return 0

    def take_uni_coin(self, card: Card):
        if len(self.tmpcards) == 3:
            raise Warning("You alreay have 3 tmp cards.")
        self.uni_coins += 1
        self.tmpcards.append(card)

    def buy(self, card: Card, noble_cards, all_coins):
        # t = self.vals - card.costs
        t = self.coins + self.cards - card.costs
        t = sum(t[t < 0])
        if self.uni_coins + t < 0:
            raise Warning(f"You do not have enough money to buy it [{str(card)}]")
        self.uni_coins += t
        all_coins[-1] -= t

        t = np.array(self.coins)
        self.coins -= card.costs
        self.coins[self.coins < 0] = 0

        all_coins[:-1] += (t - self.coins)

        self.cards[card.color] += 1
        # 在board中判断贵族卡
        # self.vals = self.coins + self.cards
        self.score += card.score
        for i, nc in enumerate(noble_cards):
            if self.take_noble_card(nc):
                noble_cards.pop(i)
                break

    def take_noble_card(self, nobel_card: NobleCard):
        t = self.cards - nobel_card.costs
        if len(t[t < 0]) > 0:
            return False
        self.score += nobel_card.score
        return True


@GAME_REGISTRY.register()
class Splendor(Game):

    Card3_icon = '\033[35;1m***\033[0m'
    Card2_icon = '\033[31;1m* *\033[0m'
    Card1_icon = '\033[32;1m * \033[0m'
    Noble_icon = '\033[33;1m-*-\033[0m'

    Color_str_to_idx = {
        'w': Color.White,
        'white': Color.White,
        'b': Color.Black,
        'black': Color.Black,
        'r': Color.Red,
        'red': Color.Red,
        'u': Color.Blue,
        'blue': Color.Blue,
        'g': Color.Green,
        'green': Color.Green,
    }

    def __init__(self, player_names):  # *** 增加输出玩家tmpcards信息, 牌库卡剩余信息. return -1改成raise
        super(Splendor, self).__init__(player_names, Player)
        self.width = 90
        self.num_players = len(player_names)

        # assert 5 > self.num_players > 1

        self.cards = [[], [], []]
        self.noble_cards_on_board = []
        self.cards_on_board = [[], [], []]
        n = 0
        if self.num_players != 4:
            n = 2
        n = 7 - n
        self.coins = np.array([n, n, n, n, n, 5], dtype=np.int32)
        self._end = False

        self.register_action(('redeem', 'r'), self._redeem, "args[1-3]. Redeem one of your tmp card.")
        self.register_action(('take', 't'), self._take_coins, "args[lowercases of colors]")
        self.register_action(('u',), self._take_uni_coins, "take uni coin, [x 1-3],[y 1-4 or none] choose a card")
        self.register_action(('buy', 'b'), self._buy, "[x 1-3] [y 1-4] buy a card")

    @classmethod
    def max_player_n(cls):
        return 4

    @classmethod
    def min_player_n(cls):
        return 2

    def _buy(self, p: Player, *args):
        # [i] [j] ...,  [i] 级卡的从左往右数第 [j] 张
        if len(args) != 2:
            raise Warning(f"Action [buy] error: args num should be 2. args[{args}]")
        args = list(args)
        for i in range(2):
            try:
                args[i] = int(args[i]) - 1
            except:
                raise Warning(f"args[{i}]: [{args[i]}] should be a number")
        if args[0] < 0 or args[0] > 2 or args[1] < 0 or args[1] >= len(self.cards_on_board[args[0]]):
            raise Warning("Index Error")
        x, y = args[0], args[1]
        card = self.cards_on_board[x][y]
        p.buy(card, self.noble_cards_on_board, self.coins)

        if len(self.cards[args[0]]) > 0:
            card = self.cards[x].pop()  # 牌库取牌
            self.cards_on_board[x][y] = card
        else:
            self.cards_on_board[x].pop(y)

        # self.coins += card.costs

    def _take_uni_coins(self, p: Player, *args):
        # [i] [j] ...,  [i] 级卡的从左往右数第 [j] 张
        # [i], 盲抵第i类卡
        if len(args) == 0:
            raise Warning("empty args.")
        if self.coins[-1] == 0:
            raise Warning("you have no uni coin.")
        if len(p.tmpcards) == 3:
            raise Warning("your already have 3 tmp cards.")
        if len(args) == 1:  # 随机在牌库选一张
            card_type = -1
            try:
                card_type = int(args[0]) - 1
            except:
                pass
            if card_type < 0 or card_type > 2:
                raise Warning("Index error, card type should be 1-3.")
            if len(self.cards[card_type]) == 0:  # 这种类型的卡已经用完了
                raise Warning(f"There are no type {card_type + 1} cards left.")
            card = self.cards[card_type].pop()  # 盲抵一手  ******判断牌库信息
        else:
            args = list(args)
            for i in range(2):
                try:
                    args[i] = int(args[i]) - 1
                except:
                    raise Warning("Args type error. Two args should be int.")
            if args[0] < 0 or args[0] > 2 or args[1] < 0 or args[1] >= len(self.cards_on_board[args[0]]):
                raise Warning(f"Index error. [x] range 1-3, [y] range 1-4.")
            card = self.cards_on_board[args[0]].pop(args[1])  # ******判断牌库信息

        p.take_uni_coin(card)
        self.coins[-1] -= 1

    def _take_coins(self, p: Player, *args, **kwargs):
        # take r
        # take r r
        # take r b
        # take r b g
        # r, red, R, ReD : red
        if len(args) == 0:
            raise Warning("args is empty.")
        coins = container()

        args = list(args)
        n = min(3, len(args))
        for i in range(n):
            if args[i] not in self.Color_str_to_idx:
                raise Warning(f"Unkown color [{args[i]}]")
            args[i] = self.Color_str_to_idx[args[i]]
            coins[args[i]] += 1

        idx = coins > 1
        if len(coins[idx]) > 0:
            if n == 3:
                raise Warning(f"args error [{args}]")  # 拿了两个相同的币+1个其他币
            if self.coins[:-1][idx] < 4:
                raise Warning("Coins number < 4")  # 要拿两个币但是剩余硬币<4

        c = self.coins[:-1] - coins
        if len(c[c < 0]) > 0:
            raise Warning(f"No coins")

        p.take_coins(coins)
        self.coins[:-1] -= coins

    def _redeem(self, p: Player, *args):
        # redeem
        # redeem 1-3
        idx = 0
        if len(args) > 0:
            try:
                idx = int(args[0]) - 1
            except:
                pass
        if idx >= len(p.tmpcards) or idx < 0:
            raise Warning(f"Index [{idx + 1}] error, you have only {len(p.tmpcards)} tmp cards.")
        p.buy(p.tmpcards[idx], self.noble_cards_on_board, self.coins)
        p.tmpcards.pop(idx)

    def is_end(self):
        return self._end

    def _set_end(self, current_player):
        # 每个move后判断是否结束，结束则is_end()返回True
        if current_player == tuple(self.players.keys())[-1]:  # 当前玩家为最后一个玩家
            score = 0
            wp = None
            for p in self.players.values():
                if p.score > score:
                    wp = p
                    score = p.score
            if wp is not None and wp.score >= 15:
                self._win_msg = f'Player {wp.name} win.'
                self._end = True

    def win_info(self):
        return self._win_msg

    def load(self):
        # noble_cards = cards_3 = cards_2 = cards_1 = []  # *****
        fpath = os.path.join('gamefiles', 'BSSR')
        if not os.path.isdir(fpath):
            raise ValueError(f"Game file path [{fpath}] is not exist.")

        noble_cards = os.path.join(fpath, 'cards_n.txt')
        cards_3 = os.path.join(fpath, 'cards_3.txt')
        cards_2 = os.path.join(fpath, 'cards_2.txt')
        cards_1 = os.path.join(fpath, 'cards_1.txt')

        required_files = [noble_cards, cards_3, cards_2, cards_1]
        self.check_before_run(required_files)
        noble_cards = self.process_file(noble_cards, NobleCard)
        cards_3 = self.process_file(cards_3, Card)
        cards_2 = self.process_file(cards_2, Card)
        cards_1 = self.process_file(cards_1, Card)

        self.cards = [cards_1, cards_2, cards_3]
        n = self.num_players + 1
        random.shuffle(noble_cards)
        for k in self.cards:
            random.shuffle(k)
        for _ in range(n):
            self.noble_cards_on_board.append(noble_cards.pop())
        for _ in range(4):
            for i in range(3):
                self.cards_on_board[i].append(self.cards[i].pop())

    @staticmethod
    def check_before_run(required_files):
        """Checks if required files exist before going deeper.
        Args:
            required_files (str or list): string file name(s).
        """
        if isinstance(required_files, str):
            required_files = [required_files]

        for fpath in required_files:
            if not os.path.exists(fpath):
                raise RuntimeError('"{}" is not found'.format(fpath))

    @staticmethod
    def process_file(fpath, card_type: type):
        cards = []
        assert isinstance(card_type, type)
        for line in open(fpath):
            line = line.strip()
            if line and not line.startswith('#'):
                cards.append(card_type(line))
        return cards

    def set_state(self, info):  # 更新on board的信息，给client 打印
        info_all = json.loads(info)
        self.noble_cards_on_board.clear()
        for v in info_all[0]:
            self.noble_cards_on_board.append(NobleCard(v))

        self.cards_on_board.clear()
        for cards in info_all[1]:
            cs = []
            for v in cards:
                cs.append(Card(v))
            self.cards_on_board.append(cs)

        self.coins = np.array(info_all[2], dtype=np.int32)
        self.players = info_all[3]
        for k in self.players:
            self.players[k] = Player(self.players[k])

    def state(self):
        # noble_cards, cards3, cards2, cards1, coins, players
        info_all = [self.noble_cards_on_board,
                    self.cards_on_board,
                    self.coins,
                    self.players]
        return json_dumps(info_all)

    '''def _info_1type_cards(self, cards):
        info = ''
        for card in cards:
            info += str(card) + '|'
        info.removesuffix('|')
        return info'''

    @staticmethod
    def write(msg):
        # 重载或重定向此函数
        print(msg)

    def show(self):
        # ClearCLI()
        self.write('+----------------------------------------------------------------------------------------+')
        self.show_cards(self.noble_cards_on_board, self.Noble_icon, True)
        self.write('+----------------------------------------------------------------------------------------+')
        self.write('|   coins        {}       {}       {}       {}       {}       {}             |'.
                   format(Color.Ground_Colors[0], Color.Ground_Colors[1],
                          Color.Ground_Colors[2], Color.Ground_Colors[3],
                          Color.Ground_Colors[4], Color.Ground_Colors[5]))
        self.write('|                  {}          {}          {}          {}          {}          {}              |'.
                   format(self.coins[0], self.coins[1], self.coins[2],
                          self.coins[3], self.coins[4], self.coins[5]))
        self.write('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_on_board[2], self.Card3_icon)
        self.write('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_on_board[1], self.Card2_icon)
        self.write('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_on_board[0], self.Card1_icon)
        self.write('|----------------------------------------------------------------------------------------|')
        self.show_players()
        self.write('+----------------------------------------------------------------------------------------+')

    def show_players(self):  # 要加上tmpcards信息
        self.write('|               {}      {}      {}      {}      {}      {}       total       |'.
                   format(Color.Ground_Colors[0], Color.Ground_Colors[1],
                          Color.Ground_Colors[2], Color.Ground_Colors[3],
                          Color.Ground_Colors[4], Color.Ground_Colors[5]))
        for player in self.players.values():  # python 3.6 以后字典是有序的
            s = '|' + player.name.ljust(15)
            coins_n = 0
            cards_n = 0
            cc = [0 for _ in range(len(Color.Ground_Colors) - 1)]
            for i in range(len(Color.Ground_Colors) - 1):
                s += '({}, {})    '.format(player.coins[i], player.cards[i])
                coins_n += player.coins[i]
                cards_n += player.cards[i]
                cc[i] += player.coins[i] + player.cards[i]
            s += '({}, {})     '.format(player.uni_coins, 0)
            coins_n += player.uni_coins
            s += '({}, {})      |'.format(coins_n, cards_n)
            # s += ' (coins,cards)|'
            self.write(s)
            s = '|       total     '
            for i in cc:
                s += '{}         '.format(i)
            s += '                     |'
            self.write(s)

    def show_cards(self, cards, icon, noble=False):
        s = '|    {}           '.format(icon)
        interval = 16
        if noble:
            s += '  '
            # interval = (self.width - len(s)) // len(self.noble_cards_on_board)
            interval = 14

        interval1 = ' ' * (interval - 8)
        interval2 = ' ' * (interval - 6)
        for card in cards:
            if noble:
                s += '({})     '.format(card.score) + interval1
            else:
                s += '({}) {}'.format(card.score, Color.Ground_Colors[card.color]) + interval1
        if noble:
            n = 5 - len(cards)
            s += ' ' * interval * n
            s = s[:-2] + '|'
        else:
            n = 4 - len(cards)
            s += ' ' * interval * n
            s += '      |'
        self.write(s)
        if not noble:
            self.write('|                                                                                        |')
        s = '|   costs'.ljust(21)
        for i in range(len(Color.Ground_Colors) - 1):
            for card in cards:
                if card.costs[i] == 0:
                    s += '      '
                else:
                    s += '{} {}'.format(card.costs[i], Color.Ground_Colors[i])
                s += interval2
            if noble:
                n = 5 - len(cards)
                s += ' ' * interval * n
                s = s[:-2] + '|'
            else:
                n = 4 - len(cards)
                s += ' ' * interval * n
                s += '    |'
            # s = s.ljust(self.width - 1) + '|'
            # self.write(s.ljust(self.width - 1), '|')
            self.write(s)
            s = '|'.ljust(21)


if __name__ == '__main__':
    cost = container()
    cost[[0, 2, 3]] = 2
    N_C = [NobleCard(cost) for _ in range(10)]
    cards3 = [Card(cost, Color.Red, 1) for i in range(10)]
    cards2 = [Card(cost, Color.Red, 1) for _ in range(10)]
    cards1 = [Card(cost, i % 5, 1) for i in range(10)]
    players = ['liujiaqi', 'leo', 'abc', 'transformer']
    board = Splendor(players)
    board.players['leo'].tmpcards.append(Card('[3,2,4,1,1] 2 3'))
    board.players['leo'].tmpcards.append(Card('[1,2,3,4,5] 3 2'))
    board.load()
    for i in range(1):
        board.show()
        print('******{}******'.format(i))
        msg = board.state()
        print(len(msg))
        print(msg)

        board.set_state(msg)

        msg = board.state()
        print(len(msg))
        print(msg)

