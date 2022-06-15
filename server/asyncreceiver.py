# 2022/5/12  0:32  liujiaqi
from .log import log
from utils import actionregister
from .manager import ServerManager


def makeint(v):
    try:
        t = int(v)
    except:
        t = None
    return t


class AsyncReceiver(actionregister.ActionRegister):
    def __init__(self, reader, writer, name, glbmanager: ServerManager):
        super(AsyncReceiver, self).__init__()
        self.reader = reader
        self.writer = writer
        self.name = name
        self.glbplayers = glbmanager.players
        self.glbgroups = glbmanager.groups
        self.glbmanager = glbmanager
        self.register_action('pStat', self.pStat)
        self.register_action('gStat', self.gStat)
        self.register_action('join', self.join)
        self.register_action('ginfo', self.ginfo)
        self.register_action('ready', self.ready)
        self.register_action('game', self.put_msg_to_game_thread)

    async def __call__(self, *args, **kwargs):
        while True:
            msg = await self.reader.read()
            if msg == "exit":
                return
            try:
                super(AsyncReceiver, self).__call__(msg)
            except Exception as e:
                log(repr(e), self.name)
            await self.writer.drain()

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
        # write(self.socket, "enum" + str(len(self.glbplayers)))
        self.writer.write("enum" + str(len(self.glbplayers)))
        selfinfo = None
        for key in self.glbplayers.players:
            if self.glbplayers.isbusy(key):
                ss = key + " b " + str(self.glbplayers[key].gid)
            else:
                ss = key + " a"
            if key == self.name:
                selfinfo = ss
            else:
                # write(self.socket, ss)
                self.writer.write(ss)
        # write(self.socket, selfinfo)
        self.writer.write(selfinfo)

    def gStat(self, *args):
        log("Made request for group Stats.", self.name)
        # write(self.socket, "enum" + str(len(self.glbgroups)))
        self.writer.write("enum" + str(len(self.glbgroups)))
        for i, t in enumerate(self.glbgroups.groups):
            # write(self.socket, str(t.gid) + ' ' + str(len(t)))
            self.writer.write(str(t.gid) + ' ' + str(len(t)))

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
                # write(self.socket, "Do nothing...")
                self.writer.write("Do nothing...")
            else:
                self.glbgroups[pgid].pop(self.name)
                # self.glbplayers.rmbusy(self.name)
                log(f"quit group {pgid}", self.name)
                # write(self.socket, f'Quit group {pgid}.')
                self.writer.write(f'Quit group {pgid}.')
        else:
            tinfo = self.glbgroups[gid]
            pgid = p.gid
            if pgid is not None:
                self.glbgroups[pgid].pop(self.name)  # 先退出原来的组
            if tinfo.push(p):
                log(f"Successfully joined group {gid}", self.name)
                # write(self.socket, f'Successfully joined group {gid}')
                self.writer.write(f'Successfully joined group {gid}')
            else:
                # write(self.socket, f'Failed to join, the group {gid} is full.')
                self.writer.write(f'Failed to join, the group {gid} is full.')

            '''if tinfo.isfull():
                write(self.socket, f'Failed to join, the group {gid} is full.')
            else:
                if p.gid is not None:
                    self.glbgroups[p.gid].pop(self.name)
                tinfo.push(p)
                # self.glbplayers.mkbusy(self.name)
                log(f"Successfully joined group {gid}", self.name)
                write(self.socket, f'Successfully joined group {gid}')'''

    def ginfo(self, *args):  # 旧方法，建议重写
        # 限制名字<=15
        if len(args) == 0 or makeint(args[0]) is None:
            gid = self.glbplayers[self.name].gid
            if gid is None:
                log("haven't joined any group.", self.name)
                # write(self.socket, 'xxx')  # xxx 让client忽略消息
                self.writer.write('xxx')
                return
        else:
            gid = int(args[0])
        log(f"made request to group {gid} info.", self.name)
        g = self.glbgroups[gid]
        # write(self.socket, f'enum {len(g) + 1}')
        self.writer.write(f'enum {len(g) + 1}')

        def genmsg(p):
            msg = p.name.ljust(20)
            if p.stat == 'r':
                msg += 'ready'
            # write(self.socket, msg)
            self.writer.write(msg)

        g.players.apply(genmsg)

        '''for p in g.players.values():
            msg = p.name.ljust(20)
            if p.stat == 'r':
                msg += 'ready'
            write(self.socket, msg)'''
        # write(self.socket, str(gid))
        self.writer.write(str(gid))

    def ready(self, *args):
        p = self.glbplayers[self.name]
        if p.gid is None:
            # write(self.socket, 'xxx')  # xxx 让client忽略消息
            return
        log(f" in group {p.gid} request to ready.", self.name)
        if p.stat != 'r':
            p.stat = 'r'
            g = self.glbgroups[p.gid]
            # write(self.socket, f'Player {self.name} ready.', True)
            self.writer.write(f'Player {self.name} ready.', 1)  # 111
            # if not g.is_alive() and g.ifstart():
            if g.ifstart():
                try:
                    g.start()
                except Exception as e:
                    log(repr(e), self.name)
                    # write(self.socket, "Game is already started.", True)
                    self.writer.write("Game is already started.", 1)  # 111
            return
        p.stat = 'b'
        # write(self.socket, f'Undo ready.')
        self.writer.write(f'Undo ready.')
