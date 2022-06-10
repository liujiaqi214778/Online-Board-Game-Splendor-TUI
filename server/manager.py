# 2022/5/16  15:53  liujiaqi
from .groups import Groups
from .players import Players
from .log import log
import time
import threading
from .socketutils import write


class ServerManager:
    def __init__(self):
        self.groups = Groups()
        self.players = Players()
        self.total = 0
        self.totalsuccess = 0
        self.START_TIME = time.perf_counter()

    def clearplayerinfo(self, name):
        p = self.players[name]
        if p is not None:
            gid = p.gid
            if gid is not None:
                self.groups[gid].pop(name)
            self.players.pop(name)
        '''gid = self.players[name].gid
        if gid is not None:
            self.groups[gid].pop(name)
        self.players.pop(name)'''

    def show_players(self):
        log("LIST OF PLAYERS:")
        cnt = 0

        def sfunc(p):
            log(f" {cnt + 1}. Player {p.name}, Status: {p.strstat()}")

        self.players.apply(sfunc)

    def report(self):
        log(f"{len(self.players)} players are online right now,")

        log(f"{len(self.players) - self.busyn()} are active.")
        log(f"{self.total} connections attempted, {self.totalsuccess} were successful")
        log(f"Server is running {threading.active_count()} threads.")
        log(f"Time elapsed since last reboot: {self.getTime()}")
        self.show_players()

    def busyn(self):
        self._busycnt = 0

        def isbusy(p):
            if p.stat != 'a':
                self._busycnt += 1

        self.players.apply(isbusy)
        return self._busycnt

    def kick(self, k):
        p = self.players[k]
        if p is not None:
            write(p.socket, "close")
            log(f"Kicking player{k}")
            self.clearplayerinfo(k)
        else:
            log(f"Player{k} does not exist")

    def kickall(self):
        log("Attempting to kick everyone.")

        def kfunc(p):
            write(p.socket, "close")
        self.players.apply(kfunc)

        self.reset()

    def kickdisconnectedplayer(self):  # 每10秒检查一次，清除断开连接的用户
        while True:
            time.sleep(10)
            for n in self.players.get_players():
                p = self.players[n]
                if p is None:
                    continue
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
                        self.clearplayerinfo(p.name)
                    except:
                        pass

    def push(self, name, sock):
        if not name or len(name) > 15 or ' ' in name:  # 名字不能带空格
            return False
        return self.players.push(name, sock)

    def getTime(self):
        sec = round(time.perf_counter() - self.START_TIME)
        minutes, sec = divmod(sec, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{days} days, {hours} hours, {minutes} minutes, {sec} seconds"

    def reset(self):
        self.players.reset()  # 一定要in-place
        self.groups.reset()
        self.total = 0
        self.totalsuccess = 0
        self.START_TIME = time.perf_counter()
