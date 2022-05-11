# 2022/5/12  0:36  liujiaqi


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
