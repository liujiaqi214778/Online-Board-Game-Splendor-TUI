# 2022/5/12  0:38  liujiaqi
from games.board import Board


# 2022/5/11  23:47  liujiaqi
import threading
import queue
import random
import time
from games.game import Game
from .log import log
from .socketutils import write
from .players import Players


class Group(threading.Thread):

    def __init__(self, gid, game):
        # 确保board是个类而不是对象, 方便玩不同类型的游戏
        if not issubclass(game, Game):
            raise ValueError("game is not a subclass of 'Game'")
        super(Group, self).__init__()
        self.gid = gid
        self.queue = None
        self.Board = game
        self.MaxN = self.Board.max_player_n()
        self.MinN = self.Board.min_player_n()
        self.players = Players(n=self.MaxN)

    def __getitem__(self, item):
        '''if item in self.players:
            return self.players[item]
        return None'''
        return self.players[item]

    def push(self, p):
        if self.players.pushp(p):
            p.gid = self.gid
            p.stat = 'b'  # 进组自动busy
            return True
        return False

    def pop(self, name):
        p = self.players.pop(name)
        if p is not None:
            p.gid = None
            p.stat = 'a'  # 退组自动active

    '''def isfull(self):
        return len(self.players) == self.MaxN'''

    def ifstart(self):
        num = len(self.players)
        if num < self.MinN:
            return False
        for n in self.players.get_players():
            p = self.players[n]
            if p is None:  # 遍历的时候有player退出了，虽然可能性很低
                num = num - 1
                if num < self.MinN:
                    return False
            elif p.stat != 'r':
                return False
        return True

    def run(self) -> None:
        self.game()
        # super(GroupInfo, self).__init__()

    def restart(self):
        if self.is_alive():
            raise RuntimeError("Game is already started")
        super(Group, self).__init__()
        self.start()

    def game(self):
        self.queue = queue.Queue()  # 由client线程发送，包括name
        # game 和其他函数由不同线程执行，考虑下self.players操作的线程安全
        names = list(self.players.get_players())
        random.shuffle(names)
        try:
            board = self._init_game(names)
        except Exception as e:
            self._send_msg_to_clients('Init Game Error:')
            self._send_msg_to_clients(repr(e))
            return

        self._send_msg_to_clients('gstart')
        self._send_board_to_clients(board)
        round_n = 0
        while True:
            if len(self.players) < self.MinN:
                # 发送中途结束消息
                log(f"group {self.gid} game 中途结束")
                self._send_msg_to_clients('Not enough players, game over.')
                return
            round_n += 1
            self._send_msg_to_clients(f'round {round_n}')
            for i, n in enumerate(board.get_players()):
                p = self[n]
                if p is None:  # 中途有玩家退出
                    board.quit(n)
                    continue
                # timout = 60
                action = self._read_action(p)
                if action is None:  # 超时
                    self._send_board_to_clients(board)
                    continue
                log(f" action: [{action}]", p.name)
                self._send_msg_to_clients(f"Player {action}")
                try:
                    self._game_move(board, action)
                    self._send_board_to_clients(board)
                    if self._game_end(board):
                        self._send_end_info_to_clients(board)
                        return
                except ValueError as e:  # 单个玩家的action有问题，不影响游戏
                    # write(p.socket, str(e), True)  # ***改成让该玩家重新输入3次
                    self._send_msg_to_clients(str(e))
                except Exception as e:
                    self._send_msg_to_clients(f'Game Error, [{repr(e)}].\nGame Over')
                    return
        # self.queue = None

    def put_player_msg(self, name, msg):
        # 由client线程判断消息类型后put给game线程
        if not self.is_alive():
            self.queue = None
            return -1
        if msg:
            self.queue.put(name + ' ' + msg)
        return 0

    def _read_action(self, p, timeout=60):
        log(f"reading action from player {p.name}")
        self._send_msg_to_clients(f"Current Player: {p.name}")
        # 改成每秒发送一次倒计时，超过60次则发送timeout
        write(p.socket, 'action', True)
        time.sleep(1)
        get_right_msg = False
        msg = None
        while not get_right_msg:
            try:
                msg = self.queue.get(timeout=timeout)  # 中途有其他信息会刷新计时器
            except:
                self._send_player_timeout_msg(p)
                return None
            args = msg.split()
            if args[0] == p.name:
                get_right_msg = True
            if args[1] == 'quit':
                self._send_msg_to_clients(f'Player {args[0]} quit the game')
                self.pop(args[0])
        # ... timer
        assert msg is not None  # 应该不会None
        # action = msg[len(p.name):].strip()
        action = msg
        return action

    def _send_msg_to_clients(self, msg):
        for name in self.players.get_players():
            p = self.players[name]
            if p is not None:
                write(p.socket, msg, True)

    def _send_player_timeout_msg(self, p):
        pass

    def _game_move(self, board, action):
        board.move(action)

        '''if game_stat < 0:  # 错误的action
            log(f" Action Error [{action}]")
            return -1
        self._send_board_to_clients(board)
        # if self._game_end(board):
        if game_stat > 0:
            self._send_end_info_to_clients(board)
            return 1
        return 0'''

    def _game_end(self, board):
        return board.is_end()

    def _init_game(self, names):
        # 要处理异常
        log(f"Group {self.gid} init game.")
        board = self.Board(names)
        '''# board.load('./configs')
        cost = container()
        cost[[0, 2, 3]] = 2
        N_C = [NobleCard(cost) for _ in range(10)]
        cards3 = [Card(cost, Color.Red, 1) for i in range(10)]
        cards2 = [Card(cost, Color.Red, 1) for _ in range(10)]
        cards1 = [Card(cost, i % 5, 1) for i in range(10)]
        board.load(N_C, cards3, cards2, cards1)'''
        board.load()
        return board

    def _send_board_to_clients(self, board):
        msg = board.info_on_board()
        log(f"send info on board: [{msg}]")
        self._send_msg_to_clients('board ' + msg)

    def _send_end_info_to_clients(self, board):
        log(f"Group {self.gid} game over.")
        # self._send_board_to_clients(board)
        self._send_msg_to_clients(f'Game over. {board.win_info()}')

    def __len__(self):
        return len(self.players)


class Groups:

    def __init__(self, n=30):
        self.maxn = n
        # 改为配置文件读游戏类型
        self.groups = [Group(i, Board) for i in range(4)]

    def create(self):
        if len(self.groups) == self.maxn:
            return -1
        self.groups.append(Group(len(self.groups), Board))
        return 0

    def reset(self):
        self.__init__(self.maxn)

    def __getitem__(self, item):
        return self.groups[item]

    def __len__(self):
        return len(self.groups)
