# 2022/5/12  0:36  liujiaqi


class PlayerInfo:
    st = {'a': 'Active',
          'b': 'Busy',
          'r': 'Ready'}

    def __init__(self, sock, name, gid=None):
        self.socket = sock
        self.name = name
        self.gid = gid
        # a: active, b: busy, r: ready
        self.stat = 'a'

    def strstat(self):
        if self.stat not in self.st:
            return 'UnKown'
        return self.st[self.stat]


class Players:
    def __init__(self, n=30):  # 加入线程安全
        self.maxn = n
        self.players = {}

    def push(self, name, sock):
        if not self.isfull() and name not in self.players:
            self.players[name] = PlayerInfo(sock, name)

    def pushp(self, p):
        assert isinstance(p, PlayerInfo)
        if not self.isfull() and p.name not in self.players:
            self.players[p.name] = p
            return True
        return False

    def pop(self, name):
        return self.players.pop(name, None)

    def apply(self, func):  # 线程安全地处理元素
        for p in self.players.values():
            func(p)

    def apply_while_true(self, func):
        for p in self.players.values():
            if not func(p):
                return

    def get_players(self):
        return tuple(self.players.keys())

    def __getitem__(self, item):
        if item in self.players:
            return self.players[item]
        return None

    def isfull(self):
        return len(self.players) == self.maxn

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

    def reset(self):
        self.__init__(self.maxn)

    '''def mkbusy(self, name):
        self._set_stat(name, 'b')

    def rmbusy(self, name):
        self._set_stat(name, 'a')

    def _set_stat(self, name, stat):
        if name in self.players:
            self.players[name].stat = stat'''

    def __len__(self):
        return len(self.players)
