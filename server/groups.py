# 2022/5/12  0:38  liujiaqi
from games import GAME_REGISTRY

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
        self.Game = game
        self.MaxN = self.Game.max_player_n()
        self.MinN = self.Game.min_player_n()
        self.players = Players(n=self.MaxN)
        self.current_player = None

    def __getitem__(self, item):
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
            if name == self.current_player:  # 玩家用其他方式退出了group
                self.queue.put(p.name)  # 防止线程继续阻塞
        return p

    '''def isfull(self):
        return len(self.players) == self.MaxN'''

    def ifstart(self):  # 去掉这个判断
        num = len(self.players)
        if num < self.MinN:
            return False

        def is_ready(p):
            return p.stat == 'r'
        return self.players.apply_while_true(is_ready)

    def run(self) -> None:
        self.game()
        self.queue = None
        # super(GroupInfo, self).__init__()

    def start(self):
        if self.is_alive():
            raise RuntimeError("Game is already started")
        super(Group, self).__init__()
        self.queue = queue.Queue()  # 由receiver线程发送，包括name
        super(Group, self).start()

    def game(self):
        # game 和其他函数由不同线程执行，考虑下self.players操作的线程安全
        names = list(self.players.get_players())
        # random.shuffle(names)
        self.current_player = None
        try:
            gameobj = self._init_game(names)
        except Exception as e:
            self._send_msg_to_clients('Init Game Error:')
            self._send_msg_to_clients(repr(e))
            return

        self._send_msg_to_clients(f'gstart {self.Game.__name__}')
        self._send_board_to_clients(gameobj)
        self._send_msg_to_clients(f"Players: {gameobj.get_players()}")
        self._send_actions_to_clients(gameobj)
        round_n = 0
        while True:
            # for i, n in enumerate(gameobj.get_players()):
            n = gameobj.next_player()  # 改为game内部定义玩家顺序
            p = self[n]
            if p is None:  # 中途有玩家退出
                gameobj.quit(n)
                if len(gameobj.get_players()) < self.MinN:  # 改为其他方式判断
                    # 发送中途结束消息
                    log(f"group {self.gid} game 中途结束")
                    self._send_msg_to_clients('gend Not enough players, game over.')
                    return
                continue
            round_n += 1
            self._send_msg_to_clients(f'round {round_n}')
            # timout = 60
            action = self._read_action(p)
            if action is None:  # 超时或当前玩家退出
                self._send_board_to_clients(gameobj)
                continue
            log(f" action: [{action}]", p.name)
            self._send_msg_to_clients(f"Player {action}")
            try:
                self._game_move(gameobj, action)
                self._send_board_to_clients(gameobj)
                if self._game_end(gameobj):
                    self._send_end_info_to_clients(gameobj)
                    return
            except Warning as e:  # 单个玩家的action有问题，不影响游戏
                # 2022/05/19 client判断action后再发送到server，这里基本不会走进来
                # write(p.socket, str(e), True)
                self._send_msg_to_clients(str(e))
            except Exception as e:
                self._send_msg_to_clients(f'gend Game Error, [{repr(e)}].\nGame Over')
                return
        # self.queue = None

    def _send_actions_to_clients(self, gameobj):
        msg = 'Game actions:\n'
        msg += gameobj.all_actions()
        self._send_msg_to_clients(msg)

    def put_player_msg(self, name, msg):
        # 由receiver线程判断消息类型后put给game线程
        if not self.is_alive():
            self.queue = None
            return -1
        if msg:
            if msg == 'quit':
                p = self.pop(name)  # read_action过程中对其他玩家只接受quit请求
                if p is not None:
                    self._send_msg_to_clients(f'Player {name} quit the game')

            elif name == self.current_player:
                self.queue.put(name + ' ' + msg)
        return 0

    def _read_action(self, p, timeout=60):
        log(f"reading action from player {p.name}")
        self._send_msg_to_clients(f"Current Player: {p.name}")
        # 改成每秒发送一次倒计时，超过60次则发送timeout
        self.current_player = p.name
        write(p.socket, 'action', True)  # action后面加等待时间
        time.sleep(1)
        msg = None
        while True:
            try:
                # 中途有其他信息会刷新计时器, 在put_player_msg只接受current player信息
                # client增加发送游戏指令前判断
                msg = self.queue.get(timeout=timeout)
                if not msg.startswith(p.name):
                    continue
                if not msg[len(p.name):].strip():
                    msg = None
            except:
                self._send_player_timeout_msg(p)
            finally:
                break

        self.current_player = None
        return msg

    def _send_msg_to_clients(self, msg):
        if not self.is_alive():
            return

        def send_msg(p):
            write(p.socket, msg, True)
        self.players.apply(send_msg)

        '''for name in self.players.get_players():
            p = self.players[name]
            if p is not None:
                write(p.socket, msg, True)'''

    def _send_player_timeout_msg(self, p):
        self._send_msg_to_clients(f"Player '{p.name} time out.'")

    def _game_move(self, gameobj, action):
        gameobj.move(action)

        '''if game_stat < 0:  # 错误的action
            log(f" Action Error [{action}]")
            return -1
        self._send_board_to_clients(board)
        # if self._game_end(board):
        if game_stat > 0:
            self._send_end_info_to_clients(board)
            return 1
        return 0'''

    def _game_end(self, gameobj):
        return gameobj.is_end()

    def _init_game(self, names):
        # 要处理异常
        log(f"Group {self.gid} init game.")
        gameobj = self.Game(names)
        '''# gameobj.load('./configs')
        cost = container()
        cost[[0, 2, 3]] = 2
        N_C = [NobleCard(cost) for _ in range(10)]
        cards3 = [Card(cost, Color.Red, 1) for i in range(10)]
        cards2 = [Card(cost, Color.Red, 1) for _ in range(10)]
        cards1 = [Card(cost, i % 5, 1) for i in range(10)]
        gameobj.load(N_C, cards3, cards2, cards1)'''
        gameobj.load()
        return gameobj

    def _send_board_to_clients(self, gameobj):
        msg = gameobj.state()
        log(f"send info on board: [{msg}]")
        self._send_msg_to_clients('board ' + msg)

    def _send_end_info_to_clients(self, gameobj):
        log(f"Group {self.gid} game over.")
        # self._send_board_to_clients(gameobj)
        self._send_msg_to_clients(f'Game over. {gameobj.win_info()}')

    def __len__(self):
        return len(self.players)


class Groups:

    def __init__(self, n=30):  # 改成 cfg.GAME.NAMES, cfg.MAX_GROUPS_N
        self.maxn = n
        # 改为配置文件读游戏类型
        gtype = GAME_REGISTRY.get('Splendor')
        self.groups = [Group(i, gtype) for i in range(4)]

    def create(self, name):
        if len(self.groups) == self.maxn:
            raise Warning(f"Max groups number is {self.maxn}.")
        self.groups.append(Group(len(self.groups), GAME_REGISTRY.get(name)))

    def reset(self):
        self.__init__(self.maxn)

    def __getitem__(self, item):
        return self.groups[item]

    def __len__(self):
        return len(self.groups)
