# 2022/5/12  0:36  liujiaqi
import socket
from .socketutils import read, write
from utils.readerswriters import ReadersWriters


class PlayerInfo:
    st = {'a': 'Active',
          'b': 'Busy',
          'r': 'Ready'}

    def __init__(self, sock: socket.socket, name, gid=None):
        self.socket = sock
        self.name = name
        self.gid = gid
        # a: active, b: busy, r: ready
        self.stat = 'a'

    def strstat(self):
        if self.stat not in self.st:
            return 'UnKown'
        return self.st[self.stat]

    def write(self, msg):
        pass

    def read(self):
        pass


class Players(ReadersWriters):
    def __init__(self, n=30):  # 加入线程安全
        super(Players, self).__init__()
        self.maxn = n
        self.players = {}

    @ReadersWriters.writer
    def push(self, name, sock):
        if not self.isfull() and name not in self.players:
            self.players[name] = PlayerInfo(sock, name)
            return True
        return False

    @ReadersWriters.writer
    def pushp(self, p):
        assert isinstance(p, PlayerInfo)
        if not self.isfull() and p.name not in self.players:
            self.players[p.name] = p
            return True
        return False

    @ReadersWriters.writer
    def pop(self, name):
        return self.players.pop(name, None)

    @ReadersWriters.reader
    def apply(self, func):  # 线程安全地处理元素
        for p in self.players.values():
            func(p)

    @ReadersWriters.reader
    def apply_while_true(self, func):
        for p in self.players.values():
            if not func(p):
                return False
        return True

    @ReadersWriters.reader
    def get_players(self):
        return tuple(self.players.keys())

    @ReadersWriters.reader
    def __getitem__(self, item):
        return self.players.get(item, None)

    def isfull(self):
        return len(self.players) == self.maxn

    @ReadersWriters.reader
    def isbusy(self, name):
        p = self[name]
        if p is None:
            return False
        return p.stat != 'a'

    @ReadersWriters.writer
    def reset(self):
        # self.__init__(self.maxn)
        self.players = {}

    @ReadersWriters.writer
    def set_stat(self, name, stat):
        if name in self.players:
            self.players[name].stat = stat

    def __len__(self):
        return len(self.players)
