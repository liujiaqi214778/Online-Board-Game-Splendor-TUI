# 2022/5/4  12:33  liujiaqi
import time

from board import ClearCLI
from sockutils import *
from utils import iterprint
import event


class Lobby:
    def __init__(self, sock, name):
        self.socket = sock
        self.username = name
        self.width = 90
        self.fps = 30
        self.lobby_instructions = {
            'help': self.showlobbyhelp,
            'join': self.joingroup,
            'refresh': self.refresh,
            'quit': self.quitserver,
            'exit': self.quitserver,
            'players': self.showplayers,
            'groups': self.showgroups,
            'send': self.sendmsgtouser,
            'ginfo': self.groupinfo,
            'ready': self.ready,
        }
        self.refresh()

    def __call__(self):
        print('Type [help] for more instructions...')
        event.event.start()
        t = 1 / self.fps
        ret = 0
        while True:
            if isDead():
                return -1
            time.sleep(t)
            # info = input()
            info = event.event.get()  # event线程接收标准输入的指令
            if info is not None:
                info = info.split()
                if len(info) == 0:
                    continue
                ins = info.pop(0)
                args = tuple(info)
                if ins not in self.lobby_instructions:
                    print('Error... [{}] is not exist.'.format(ins))
                    self.lobby_instructions['help']()
                    continue
                r = self.lobby_instructions[ins](*args)
                if r is not None and r < 0:
                    ret = r
                    break

            msg = active_msg_reciever.read()
            if msg is not None:
                if msg == "close":
                    ret = -1
                    break
                if msg.startswith('game'):
                    self.game()
        event.event.end()
        return ret

    @classmethod
    def showlobbyhelp(cls, *args):
        print('[join] [group no.] to join a group. If gid is out of range, that means quit current group.')
        print('[send] [user ID or user name] to send a message.')
        print('[refresh] to refresh the lobby, show all players and groups.')
        print('[quit] or [exit] to disconnect the server.')
        print('[players] to display all online players.')
        print('[groups] to display all groups on server (no more than 30).')
        print('[ginfo] [gid] show gid info. If gid is None, show the info of the group you joined.')
        print("[ready] Update your status to 'ready' if you are in a group. Undo ready if you are ready.")

    def groupinfo(self, *args):
        # all players in same group, and is or not ready.
        gid = ''
        if len(args) > 0:
            try:
                gid = int(args[0])
            except:
                gid = ''
        msglist = getmsgall(self.socket, f'ginfo {gid}')
        if msglist is None:
            return -2
        if len(msglist) == 0:
            print("You haven't joined any group yet.")
            return 0
        self._showginfo(msglist)

    def ready(self, *args):
        msglist = getmsgall(self.socket, 'ready')
        if msglist is None:
            return -2
        if len(msglist) == 0:
            print("You haven't joined any group yet.")
            return 0
        ClearCLI()
        self.groupinfo()
        msg = msglist[0]
        print(msg)

    def game(self, *args):
        print('start game....')

    def _showginfo(self, msglist):
        gid = msglist.pop()
        print('+' + '-' * (self.width - 2) + '+')
        print(f'| Group [{gid}] Information'.ljust(self.width - 1) + '|')
        print('+' + '-' * (self.width - 2) + '+')
        iterprint(msglist, self.width, idx=True)
        print('+' + '-' * (self.width - 2) + '+')

    def joingroup(self, *args):
        if len(args) == 0:
            print('There is no group number behind [join].')
            return 0
        # server 一个group -> 一个board -> 多个user
        try:
            gid = int(args[0])
        except:
            print('Table id should be a number.')
            return 0
        write(self.socket, f"join {gid}")
        msg = read()
        if msg == 'close':
            return -1
        self.refresh()
        self.groupinfo()
        print(msg)
        return 0

    def refresh(self, *args):
        ClearCLI()
        self.showplayers()
        self.showgroups()

    def showplayers(self, *args):
        playerlist = getmsgall(self.socket, 'pStat')
        if playerlist is None:
            return -2
        # player info : name, status, group(if busy)
        width = 90
        print('+' + '-' * (width - 2) + '+')
        selfinfo = [playerlist.pop()]
        selfinfo.extend(playerlist)
        playerlist = selfinfo
        print('| You Are {}'.format(self.username).ljust(width - 1) + '|')
        print('| List of Players:'.ljust(width - 1) + '|')
        newline = False
        s = '|'
        for cnt, player in enumerate(playerlist):
            info = player.split()
            s += ' {}. {}  '.format(cnt + 1, info[0]).ljust(25)
            stat = info[1]
            if stat == "a":
                s += 'ACTIVE'
            elif stat == "b":
                s += 'BUSY(group {})'.format(info[2])
            s = s.ljust(50)
            if not newline:
                newline = not newline
                continue
            newline = False
            print(s.ljust(89) + '|')
            s = '|'
        if newline:
            print(s.ljust(89) + '|')
        print('+' + '-' * (width - 2) + '+')
        return 0

    def showgroups(self, *args):
        groups = getmsgall(self.socket, 'gStat')
        if groups is None:
            return -2
        width = 90
        # group info: id, 人数,
        # 服务器重启开4个桌
        print('+' + '-' * (width - 2) + '+')
        print('| List of groups:'.ljust(width - 1) + '|')
        s = '|'
        i = 0
        for group in groups:
            info = group.split()
            s += ' group {}    num: {} '.format(info[0], info[1]).ljust(15)
            if int(info[1]) >= 4:
                s += ' (FULL) '
            else:
                s += '        '
            s += '|'
            if not i == 2:
                i = (i + 1) % 3
                continue
            i = 0
            s = s[:-1]
            print(s.ljust(width - 1) + '|')
            s = '|'
        if not i == 0:
            print(s.ljust(width - 1) + '|')
        print('+' + '-' * (width - 2) + '+')
        return 0

    def quitserver(self, *args):
        write(self.socket, "quit")
        return -1

    def sendmsgtouser(self, *args):
        pass
