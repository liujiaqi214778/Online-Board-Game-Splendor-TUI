# 2022/5/3  20:56  liujiaqi
"""
This file is a part of My-PyChess application.
To run the online server, run this script.

For more information, see onlinehowto.txt

IMPORTANT NOTE:
    Server.py needs atleast Python v3.6 to work.
"""

import queue
import random
import socket
import threading
import time
from urllib.request import urlopen
from board import Board, container, Card, NobleCard, Color

# These are constants that can be modified by users. Default settings
# are given. Do not change if you do not know what you are doing.
LOG = False
IPV6 = False

# =====================================================
#        DO NOT MODIFY ANYTHING BELOW THIS!!
# =====================================================

# Define other constants
VERSION = "v1.0"
PORT = 26103
START_TIME = time.perf_counter()
LOGFILENAME = time.asctime().replace(" ", "_").replace(":", "-")


def makeint(v):
    try:
        t = int(v)
    except:
        t = None
    return t


# A function to display elapsed time in desired format.
def getTime():
    sec = round(time.perf_counter() - START_TIME)
    minutes, sec = divmod(sec, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return f"{days} days, {hours} hours, {minutes} minutes, {sec} seconds"


# A function to get IP address. It can give public IP or private.
def getIp(public):
    if public:
        try:
            ip = urlopen("https://api64.ipify.org").read().decode()
        except:
            ip = "127.0.0.1"

    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
    return ip


# A function to Log/Print text. Used instead of print()
def log(data, key=None, adminput=False):
    global logQ
    if adminput:
        text = ""
    elif key is None:
        text = "SERVER: "
    else:
        text = f"Player {key}: "

    if data is not None:
        text += data
        if not adminput:
            print(text)

        if LOG:
            logQ.put(time.asctime() + ": " + text + "\n")
    else:
        logQ.put(None)


# Used instead of sock.recv(), because it returns the decoded message, handles
# TCP packet loss, timeout and other useful stuff
def read(sock, timeout=None):
    try:
        sock.settimeout(timeout)
        msg = sock.recv(4096).decode("utf-8").strip()

    except:
        msg = "quit"

    if msg:
        return msg
    return "quit"


# A function to message the server, this is used instead of socket.send()
# beacause it buffers the message, handles packet loss and does not raise
# exception if message could not be sent
def write(sock, msg, prefix=False):
    if msg:
        if prefix:
            msg = '@' + msg + '@'
        buffedmsg = msg + (" " * (4096 - len(msg)))
        try:
            sock.sendall(buffedmsg.encode("utf-8"))
        except:
            pass


class PlayerInfo:
    def __init__(self, sock, name, gid=None):
        self.socket = sock
        self.name = name
        self.gid = gid
        # a: active, b: busy, r: ready
        self.stat = 'a'


class GroupInfo(threading.Thread):

    def __init__(self, gid, board: type):
        # 确保board是个类而不是对象, 方便玩不同类型的游戏
        assert isinstance(board, type)
        super(GroupInfo, self).__init__()
        self.gid = gid
        self.players = {}
        self.queue = None
        self.Board = board
        self.MaxN = self.Board.MaxN
        self.MinN = self.Board.MinN

    def __getitem__(self, item):
        if item in self.players:
            return self.players[item]
        return None

    def push(self, p):
        if p.name not in self.players and not self.isfull():
            p.gid = self.gid
            p.stat = 'b'  # 进组自动busy
            self.players[p.name] = p

    def pop(self, name):
        p = self.players.pop(name, None)
        if p is not None:
            p.gid = None
            p.stat = 'a'  # 退组自动active

    def isfull(self):
        return len(self.players) == self.MaxN

    def ifstart(self):
        if len(self.players) < self.MinN:
            return False
        for p in self.players.values():
            if p.stat != 'r':
                return False
        return True

    def run(self):
        self.queue = queue.Queue()  # 由client线程发送，包括name
        # game 和其他函数由不同线程执行，考虑下self.players操作的线程安全
        names = []
        for p in self.players.values():
            names.append(p.name)
            # 先给所有玩家发送 active msg
            write(p.socket, 'game', True)
        random.shuffle(names)
        num = len(names)
        board = self._init_game(names)
        self._send_board_to_clients(board)
        while True:
            if num < self.MinN:
                # 发送中途结束消息
                self._send_board_to_clients(board)
                log(f"group {self.gid} game 中途结束")
                return
            for i, n in enumerate(names):
                if n is None:
                    continue
                p = self[n]
                if p is None:  # 中途有玩家退出
                    names[i] = None
                    num -= 1
                    continue
                action = self._read_action(p)
                self._send_board_to_clients(board)
                if action is None:  # 超时
                    continue
                log(f" action: [{action}]", p.name)
                if self._game_move(board, action) > 0:  # 游戏结束
                    return
        # self.queue = None

    def put_player_msg(self, name, msg):
        # 由client线程判断消息类型后put给game线程
        if not self.is_alive():
            self.queue = None
            return -1
        self.queue.put(name + ' ' + msg)
        return 0

    def _read_action(self, p):
        # 改成每秒发送一次倒计时，超过60次则发送timeout
        write(p.socket, 'action', True)
        time.sleep(1)
        get_right_msg = False
        msg = None
        while not get_right_msg:
            try:
                msg = self.queue.get(timeout=60)
            except:
                self._send_player_timeout_msg(p)
                return None
            if msg.startswith(p.name):
                get_right_msg = True
        # ... timer
        assert msg is not None  # 应该不会None
        # action = msg[len(p.name):].strip()
        action = msg
        return action

    def _send_player_timeout_msg(self, p):
        pass

    def _game_move(self, board, action):
        game_stat = board.move(action)
        if game_stat < 0:  # 错误的action
            log(f" Action Error [{action}]")
            return -1
        self._send_board_to_clients(board)
        # if self._game_end(board):
        if game_stat > 0:
            self._send_end_info_to_clients(board)
            return 1
        return 0

    def _game_end(self, board):
        # ...
        ret = []
        return ret

    def _init_game(self, names):
        log(f"Group {self.gid} init game.")
        board = self.Board(names)
        # board.load('./configs')
        cost = container()
        cost[[0, 2, 3]] = 2
        N_C = [NobleCard(cost) for _ in range(10)]
        cards3 = [Card(cost, Color.Red, 1) for i in range(10)]
        cards2 = [Card(cost, Color.Red, 1) for _ in range(10)]
        cards1 = [Card(cost, i % 5, 1) for i in range(10)]
        board.load(N_C, cards3, cards2, cards1)
        return board

    def _send_board_to_clients(self, board):
        msg = board.info_on_board()
        log(f"send info on board: [{msg}]")
        for name in self.players:
            p = self.players[name]
            write(p.socket, 'board ' + msg, True)

    def _send_end_info_to_clients(self, board):
        log(f"Group {self.gid} game over.")
        self._send_board_to_clients(board)
        for name in self.players:
            p = self.players[name]
            write(p.socket, 'gend Game over', True)

    def __len__(self):
        return len(self.players)


class Players:
    MaxN = 30

    def __init__(self):
        self.players = {}

    def push(self, name, sock):
        if name not in self.players:
            self.players[name] = PlayerInfo(sock, name)

    def pop(self, name):
        self.players.pop(name, None)

    def __getitem__(self, item):
        if item in self.players:
            return self.players[item]
        return None

    def isfull(self):
        return len(self.players) == self.MaxN

    def isbusy(self, name):
        p = self[name]
        if p is None:
            return False
        return p.stat != 'a'

    def busyn(self):
        cnt = 0
        for p in self.players.values():
            if p.stat != 'a':
                cnt += 1
        return cnt

    '''def mkbusy(self, name):
        self._set_stat(name, 'b')

    def rmbusy(self, name):
        self._set_stat(name, 'a')

    def _set_stat(self, name, stat):
        if name in self.players:
            self.players[name].stat = stat'''

    def __len__(self):
        return len(self.players)


class Groups:
    MaxN = 30

    def __init__(self):
        self.groups = [GroupInfo(i, Board) for i in range(4)]

    def create(self):
        if len(self.groups) == self.MaxN:
            return -1
        self.groups.append(GroupInfo(len(self.groups), Board))
        return 0

    def __getitem__(self, item):
        return self.groups[item]

    def __len__(self):
        return len(self.groups)


# Initialise a few global variables
end = False
lock = False
logQ = queue.Queue()
players = Players()
groups = Groups()
total = totalsuccess = 0


def clearplayerinfo(name, pall, gall):
    gid = pall[name].gid
    if gid is not None:
        gall[gid].pop(name)
    pall.pop(name)


class Client:
    def __init__(self, sock, name):
        self.socket = sock
        self.name = name
        self.funcs = {
            'pStat': self.pStat,
            'gStat': self.gStat,
            'join': self.join,
            'ginfo': self.ginfo,
            'ready': self.ready,
            'game': self.put_msg_to_game_thread,
        }

    def __call__(self):
        while True:
            msg = read(self.socket)
            if msg == "quit":
                return
            info = msg.split()
            if len(info) == 0:
                continue
            ins = info.pop(0)
            args = tuple(info)
            if ins not in self.funcs:
                log(f"Unkonw instruction [{ins}].", self.name)
                continue
            ret = self.funcs[ins](*args)
            if ret is not None and ret < 0:
                return ret

    def put_msg_to_game_thread(self, *args):
        gid = players[self.name].gid
        if gid is None:
            log("send a game msg but he/she is not in a group/game.", self.name)
            return
        if len(args) == 0:
            log("send a game msg but the msg is empty.", self.name)
            return

        g = groups[gid]
        if g.put_player_msg(self.name, ' '.join(args)) < 0:
            log("send a game msg but the game is over.", self.name)

    def pStat(self, *args):
        log("Made request for players Stats.", self.name)
        write(self.socket, "enum" + str(len(players)))
        selfinfo = None
        for key in players.players:
            if players.isbusy(key):
                ss = key + " b " + str(players[key].gid)
            else:
                ss = key + " a"
            if key == self.name:
                selfinfo = ss
            else:
                write(self.socket, ss)
        write(self.socket, selfinfo)

    def gStat(self, *args):
        log("Made request for group Stats.", self.name)
        write(self.socket, "enum" + str(len(groups)))
        for i, t in enumerate(groups.groups):
            write(self.socket, str(t.gid) + ' ' + str(len(t)))

    def join(self, *args):
        # join [gid], gid out of range means quit.
        p = players[self.name]
        if len(args) == 0:
            return
        gid = int(args[0])
        log(f"Made request to join group {gid}", self.name)
        if gid >= len(groups) or gid < 0:  # quit
            pgid = p.gid
            if pgid is None:
                write(self.socket, "Do nothing...")
            else:
                groups[pgid].pop(self.name)
                # players.rmbusy(self.name)
                log(f"quit group {pgid}", self.name)
                write(self.socket, f'Quit group {pgid}.')
        else:
            tinfo = groups[gid]
            if tinfo.isfull():
                write(self.socket, f'Failed to join, the group {gid} is full.')
            else:
                if p.gid is not None:
                    groups[p.gid].pop(self.name)
                tinfo.push(p)
                # players.mkbusy(self.name)
                log(f"Successfully joined group {gid}", self.name)
                write(self.socket, f'Successfully joined group {gid}')

    def ginfo(self, *args):
        # 限制名字<=15
        if len(args) == 0 or makeint(args[0]) is None:
            gid = players[self.name].gid
            if gid is None:
                log("haven't joined any group.", self.name)
                write(self.socket, 'xxx')  # xxx 让client忽略消息
                return
        else:
            gid = int(args[0])
        log(f"made request to group {gid} info.", self.name)
        g = groups[gid]
        write(self.socket, f'enum {len(g) + 1}')
        for p in g.players.values():
            msg = p.name.ljust(20)
            if p.stat == 'r':
                msg += 'ready'
            write(self.socket, msg)
        write(self.socket, str(gid))

    def ready(self, *args):
        p = players[self.name]
        if p.gid is None:
            write(self.socket, 'xxx')  # xxx 让client忽略消息
            return
        log(f" in group {p.gid} request to ready.", self.name)
        if p.stat != 'r':
            p.stat = 'r'
            g = groups[p.gid]
            write(self.socket, f'Player {self.name} ready.', True)
            # if not g.is_alive() and g.ifstart():
            if g.ifstart():
                try:
                    g.start()
                except:
                    write(self.socket, "Game is already started.", True)
            return
        p.stat = 'b'
        write(self.socket, f'Undo ready.')


# A thread to log all the texts. Flush from logQ.
def logThread():
    global logQ
    while True:
        time.sleep(1)
        with open("SERVER_LOG_" + LOGFILENAME + ".txt", "a") as f:
            while not logQ.empty():
                data = logQ.get()
                if data is None:
                    return
                else:
                    f.write(data)


# This is a Thread that runs in background to remove disconnected people
def kickDisconnectedThread():
    global players
    while True:
        time.sleep(10)
        for p in players.players.values():
            try:
                ret = p.socket.send(b"........")
            except:
                ret = 0

            if ret > 0:
                cntr = 0
                diff = 8
                while True:
                    cntr += 1
                    if cntr == 8:
                        ret = 0
                        break

                    if ret == diff:
                        break
                    diff -= ret

                    try:
                        ret = p.sock.send(b"." * diff)
                    except:
                        ret = 0
                        break

            if ret == 0:
                log(f"Player {p.name} got disconnected, removing from player list")
                try:
                    # players.pop(p.name)
                    clearplayerinfo(p.name, players, groups)
                except:
                    pass


# This is a Thread that runs in background to collect user input commands
def adminThread():
    global end, lock, players, groups
    while True:
        msg = input().strip()
        log(msg, adminput=True)

        if msg == "report":
            log(f"{len(players)} players are online right now,")
            log(f"{len(players) - players.busyn()} are active.")
            log(f"{total} connections attempted, {totalsuccess} were successful")
            log(f"Server is running {threading.active_count()} threads.")
            log(f"Time elapsed since last reboot: {getTime()}")
            if players:
                log("LIST OF PLAYERS:")
                for cnt, name in enumerate(players.players):
                    if not players.isbusy(name):
                        log(f" {cnt + 1}. Player {name}, Status: Active")
                    else:
                        log(f" {cnt + 1}. Player {name}, Status: Busy")

        elif msg == "mypublicip":
            log("Determining public IP, please wait....")
            PUBIP = getIp(public=True)
            if PUBIP == "127.0.0.1":
                log("An error occurred while determining IP")

            else:
                log(f"This machine has a public IP address {PUBIP}")

        elif msg == "lock":
            if lock:
                log("Aldready in locked state")
            else:
                lock = True
                log("Locked server, no one can join now.")

        elif msg == "unlock":
            if lock:
                lock = False
                log("Unlocked server, all can join now.")
            else:
                log("Aldready in unlocked state.")

        elif msg.startswith("kick "):
            for k in msg[5:].split():
                sock = players[k].socket
                if sock is not None:
                    write(sock, "close")
                    log(f"Kicking player{k}")
                else:
                    log(f"Player{k} does not exist")

        elif msg == "kickall":
            log("Attempting to kick everyone.")
            for p in players.players.values():
                write(p.socket, "close")
            players = Players()
            groups = Groups()

        elif msg == "quit":
            lock = True
            log("Attempting to kick everyone.")
            for p in players.players.values():
                write(p.socket, "close")
            # players = Players()

            log("Exiting application - Bye")
            log(None)

            end = True
            if IPV6:
                with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                    s.connect(("::1", PORT, 0, 0))
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", PORT))
            return

        else:
            log(f"Invalid command entered ('{msg}').")
            log("See 'onlinehowto.txt' for help on how to use the commands.")


# Does the initial checks and lets players in.
def initPlayerThread(sock):
    global players, total, totalsuccess
    log("New client is attempting to connect.")
    total += 1

    def judge_name(name):
        if name in players.players or len(name) > 15:
            return False
        players.push(name, sock)
        return True

    if read(sock, 3) != "PyGame":
        log("Client sent invalid header, closing connection.")
        write(sock, "errVer")

    elif read(sock, 3) != VERSION:
        log("Client sent invalid version info, closing connection.")
        write(sock, "errVer")

    elif players.isfull():
        log("Server is busy, closing new connections.")
        write(sock, "errBusy")

    elif lock:
        log("SERVER: Server is locked, closing connection.")
        write(sock, "errLock")

    else:
        name = read(sock, 3)
        if not judge_name(name):
            log("Client sent invalid user name (length > 15 or already exist), closing connection.")
            write(sock, "errName")
        else:
            totalsuccess += 1
            # key = genKey()
            log(f"Connection Successful, user name - {name}")

            write(sock, "succ")
            Client(sock, name)()
            write(sock, "close")
            log(f"Player {name} has Quit")

            try:
                clearplayerinfo(name, players, groups)
            except:
                pass
            # players.rmbusy(name)
    sock.close()


# Initialize the main socket
log(f"Welcome to My-game Server, {VERSION}\n")
log("INITIALIZING...")

if IPV6:
    log("IPv6 is enabled. This is NOT the default configuration.")

    mainSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    mainSock.bind(("::", PORT, 0, 0))
else:
    log("Starting server with IPv4 (default) configuration.")
    mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainSock.bind(("0.0.0.0", PORT))

    IP = getIp(public=False)
    if IP == "127.0.0.1":
        log("This machine does not appear to be connected to a network.")
        log("With this limitation, you can only serve the clients ")
        log("who are on THIS machine. Use IP address 127.0.0.1\n")

    else:
        log(f"This machine has a local IP address - {IP}")
        log("USE THIS IP IF THE CLIENT IS ON THE SAME NETWORK.")
        log("For more info, read file 'onlinehowto.txt'\n")

mainSock.listen(16)
log("Successfully Started.")
log(f"Accepting connections on port {PORT}\n")

threading.Thread(target=adminThread).start()
threading.Thread(target=kickDisconnectedThread, daemon=True).start()
if LOG:
    log("Logging is enabled. Starting to log all output")
    threading.Thread(target=logThread).start()

while True:
    s, _ = mainSock.accept()
    if end:
        break

    threading.Thread(target=initPlayerThread, args=(s,), daemon=True).start()
mainSock.close()
