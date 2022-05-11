# 2022/5/12  0:32  liujiaqi
from socketutils import read, write
from log import log
from players import Players
from groups import Groups


def makeint(v):
    try:
        t = int(v)
    except:
        t = None
    return t


class User:
    def __init__(self, sock, name, glbplayers: Players, glbgroups: Groups):
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
        self.glbplayers = glbplayers
        self.glbgroups = glbgroups

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
        gid = self.glbplayers[self.name].gid
        if gid is None:
            log("send a game msg but he/she is not in a group/game.", self.name)
            return
        if len(args) == 0:
            log("send a game msg but the msg is empty.", self.name)
            return

        g = self.glbgroups[gid]
        if g.put_player_msg(self.name, ' '.join(args)) < 0:
            log("send a game msg but the game is over.", self.name)

    def pStat(self, *args):
        log("Made request for players Stats.", self.name)
        write(self.socket, "enum" + str(len(self.glbplayers)))
        selfinfo = None
        for key in self.glbplayers.players:
            if self.glbplayers.isbusy(key):
                ss = key + " b " + str(self.glbplayers[key].gid)
            else:
                ss = key + " a"
            if key == self.name:
                selfinfo = ss
            else:
                write(self.socket, ss)
        write(self.socket, selfinfo)

    def gStat(self, *args):
        log("Made request for group Stats.", self.name)
        write(self.socket, "enum" + str(len(self.glbgroups)))
        for i, t in enumerate(self.glbgroups.groups):
            write(self.socket, str(t.gid) + ' ' + str(len(t)))

    def join(self, *args):
        # join [gid], gid out of range means quit.
        p = self.glbplayers[self.name]
        if len(args) == 0:
            return
        gid = int(args[0])
        log(f"Made request to join group {gid}", self.name)
        if gid >= len(self.glbgroups) or gid < 0:  # quit
            pgid = p.gid
            if pgid is None:
                write(self.socket, "Do nothing...")
            else:
                self.glbgroups[pgid].pop(self.name)
                # self.glbplayers.rmbusy(self.name)
                log(f"quit group {pgid}", self.name)
                write(self.socket, f'Quit group {pgid}.')
        else:
            tinfo = self.glbgroups[gid]
            if tinfo.isfull():
                write(self.socket, f'Failed to join, the group {gid} is full.')
            else:
                if p.gid is not None:
                    self.glbgroups[p.gid].pop(self.name)
                tinfo.push(p)
                # self.glbplayers.mkbusy(self.name)
                log(f"Successfully joined group {gid}", self.name)
                write(self.socket, f'Successfully joined group {gid}')

    def ginfo(self, *args):
        # 限制名字<=15
        if len(args) == 0 or makeint(args[0]) is None:
            gid = self.glbplayers[self.name].gid
            if gid is None:
                log("haven't joined any group.", self.name)
                write(self.socket, 'xxx')  # xxx 让client忽略消息
                return
        else:
            gid = int(args[0])
        log(f"made request to group {gid} info.", self.name)
        g = self.glbgroups[gid]
        write(self.socket, f'enum {len(g) + 1}')
        for p in g.players.values():
            msg = p.name.ljust(20)
            if p.stat == 'r':
                msg += 'ready'
            write(self.socket, msg)
        write(self.socket, str(gid))

    def ready(self, *args):
        p = self.glbplayers[self.name]
        if p.gid is None:
            write(self.socket, 'xxx')  # xxx 让client忽略消息
            return
        log(f" in group {p.gid} request to ready.", self.name)
        if p.stat != 'r':
            p.stat = 'r'
            g = self.glbgroups[p.gid]
            write(self.socket, f'Player {self.name} ready.', True)
            # if not g.is_alive() and g.ifstart():
            if g.ifstart():
                try:
                    g.restart()
                except Exception as e:
                    log(repr(e), self.name)
                    write(self.socket, "Game is already started.", True)
            return
        p.stat = 'b'
        write(self.socket, f'Undo ready.')
