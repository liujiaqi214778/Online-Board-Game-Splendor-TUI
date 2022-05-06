import os
import platform
import time
import numpy as np

from colorama import init
from enum import Enum

init(autoreset=True)


def ClearCLI():
    system = platform.system()
    if system == u'Windows':
        os.system('cls')
    else:
        os.system('clear')


class Color:  # (Enum):
    White = 0
    Black = 1
    Red = 2
    Blue = 3
    Green = 4
    Yellow = 5


def container():
    # Yellow 为万能币
    # return np.array([0 for _ in range(len(Color.__members__) - 1)])
    return np.array([0 for _ in range(Color.Yellow)])


class Card:
    def __init__(self, costs, color, score):
        self.costs = costs  # numpy array
        self.color = color
        self.score = score


class NobleCard:
    def __init__(self, costs):
        self.score = 3
        self.costs = costs


class Player:
    def __init__(self, name):
        self.name = name
        self.coins = container()
        self.cards = container()
        self.vals = container()
        self.uni_coins = 0
        self.score = 0
        self.tmpcards = []

    def redeem(self, idx):
        if idx >= len(self.tmpcards):
            print('')
            return -1
        ret = self.buy(self.tmpcards[idx])
        if not ret < 0:
            self.tmpcards.pop(idx)
        return ret

    def take_coins(self, coins):
        if sum(self.coins) + sum(coins) > 10:
            return -1
        self.coins += coins
        self.vals += coins
        return 0

    def take_uni_coin(self, card):
        if len(self.tmpcards) == 3:
            return -1
        self.uni_coins += 1
        self.tmpcards.append(card)
        return 0

    def buy(self, card):
        t = self.vals - card.costs
        t = sum(t[t < 0])
        if self.uni_coins + t < 0:
            return -1
        self.uni_coins += t
        self.coins -= card.costs
        self.coins[self.coins < 0] = 0
        self.cards[card.color] += 1
        # 在board中判断贵族卡
        self.vals = self.coins + self.cards
        self.score += card.score
        if self.score >= 15:
            return 1
        return 0


class Board:
    White = 'W\033[1;30;47m   \033[0m'
    Black = 'B\033[40;1m   \033[0m'
    Red = 'R\033[41;1m   \033[0m'
    Blue = 'U\033[44;1m   \033[0m'
    Green = 'G\033[42;1m   \033[0m'
    Yellow = 'Y\033[43;1m   \033[0m'
    Ground_Colors = [White, Black, Red, Blue, Green, Yellow]

    Card3_icon = '\033[35;1m***\033[0m'
    Card2_icon = '\033[31;1m* *\033[0m'
    Card1_icon = '\033[32;1m * \033[0m'
    Noble_icon = '\033[33;1m-*-\033[0m'

    def __init__(self, players, noble_cards, cards_3, cards_2, cards_1):
        self.width = 90
        self.num_players = len(players)
        self.players = []
        for name in players:
            self.players.append(Player(name))

        assert 5 > self.num_players > 1
        n = self.num_players + 1
        # self.noble_cards = noble_cards
        self.cards_3 = cards_3
        self.cards_2 = cards_2
        self.cards_1 = cards_1
        self.noble_cards_on_board = []
        self.cards_3_on_board = []
        self.cards_2_on_board = []
        self.cards_1_on_board = []
        for _ in range(n):
            self.noble_cards_on_board.append(noble_cards.pop())

        for _ in range(4):
            self.cards_3_on_board.append(cards_3[-1])
            cards_3.pop()
            self.cards_2_on_board.append(cards_2[-1])
            cards_2.pop()
            self.cards_1_on_board.append(cards_1[-1])
            cards_1.pop()

        self.reset()

    def reset(self):
        n = 0
        if self.num_players != 4:
            n = 2
        self.W_n = 7 - n
        self.B_n = 7 - n
        self.R_n = 7 - n
        self.U_n = 7 - n
        self.G_n = 7 - n
        self.Y_n = 5
        self.show()

    def show(self):
        ClearCLI()
        print('+----------------------------------------------------------------------------------------+')
        self.show_cards(self.noble_cards_on_board, self.Noble_icon, True)
        print('+----------------------------------------------------------------------------------------+')
        print('|   coins        {}       {}       {}       {}       {}       {}             |'.
              format(self.White, self.Black, self.Red, self.Blue, self.Green, self.Yellow))
        print('|                  {}          {}          {}          {}          {}          {}              |'.
              format(self.W_n, self.B_n, self.R_n, self.U_n, self.G_n, self.Y_n))
        print('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_3_on_board, self.Card3_icon)
        print('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_2_on_board, self.Card2_icon)
        print('|----------------------------------------------------------------------------------------|')
        self.show_cards(self.cards_1_on_board, self.Card1_icon)
        print('|----------------------------------------------------------------------------------------|')
        self.show_players()
        print('+----------------------------------------------------------------------------------------+')

    def show_players(self):
        print('|               {}      {}      {}      {}      {}      {}       total       |'.
              format(self.White, self.Black, self.Red, self.Blue, self.Green, self.Yellow))
        for player in self.players:
            s = '|' + player.name.ljust(15)
            coins_n = 0
            cards_n = 0
            cc = [0 for _ in range(len(self.Ground_Colors) - 1)]
            for i in range(len(self.Ground_Colors) - 1):
                s += '({}, {})    '.format(player.coins[i], player.cards[i])
                coins_n += player.coins[i]
                cards_n += player.cards[i]
                cc[i] += player.coins[i] + player.cards[i]
            s += '({}, {})     '.format(player.uni_coins, 0)
            coins_n += player.uni_coins
            s += '({}, {})      |'.format(coins_n, cards_n)
            # s += ' (coins,cards)|'
            print(s)
            s = '|       total     '
            for i in cc:
                s += '{}         '.format(i)
            s += '                     |'
            print(s)

    def show_cards(self, cards, icon, noble=False):
        s = '|    {}           '.format(icon)
        interval = 16
        if noble:
            s += '  '
            # interval = (self.width - len(s)) // len(self.noble_cards_on_board)
            interval = 14

        interval1 = ' '*(interval - 8)
        interval2 = ' '*(interval - 6)
        for card in cards:
            if noble:
                s += '({})     '.format(card.score) + interval1
            else:
                s += '({}) {}'.format(card.score, self.Ground_Colors[card.color]) + interval1
        if noble:
            n = 5 - len(cards)
            s += ' ' * interval * n
            s = s[:-2] + '|'
        else:
            n = 4 - len(cards)
            s += ' ' * interval * n
            s += '      |'
        print(s)
        if not noble:
            print('|                                                                                        |')
        s = '|   costs'.ljust(21)
        for i in range(len(self.Ground_Colors) - 1):
            for card in cards:
                if card.costs[i] == 0:
                    s += '      '
                else:
                    s += '{} {}'.format(card.costs[i], self.Ground_Colors[i])
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
            # print(s.ljust(self.width - 1), '|')
            print(s)
            s = '|'.ljust(21)


if __name__ == '__main__':
    cost = container()
    cost[[0, 2, 3]] = 2
    N_C = [NobleCard(cost) for _ in range(10)]
    cards3 = [Card(cost, Color.Red, 1) for i in range(10)]
    cards2 = [Card(cost, Color.Red, 1) for _ in range(10)]
    cards1 = [Card(cost, i % 5, 1) for i in range(10)]
    players = ['liujiaqi', 'leo']
    board = Board(players, N_C, cards3, cards2, cards1)
    for i in range(10):
        time.sleep(1)
        board.show()
        print('******{}******'.format(i))
