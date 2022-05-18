# 2022/5/4  12:33  liujiaqi
import time

from games.board import Board
from .sockutils import *
from utils.utils import iterprint, ClearCLI
from utils import event, actionregister


class Lobby(actionregister.ActionRegister):
    def __init__(self, sock, name):
        super(Lobby, self).__init__()
        self.socket = sock
        self.username = name
        self.width = 90
        self.fps = 30

        # 所有注册的方法重写下，不要read
        self.register_action('help', self.showlobbyhelp)
        self.register_action('join', self.joingroup,
                             'args[group no.] to join a group. If gid is out of range, that means quit current group.')
        self.register_action('refresh', self.refresh, 'refresh the lobby, show all players and groups.')
        self.register_action('exit', self.quitserver, 'disconnect the server.')
        self.register_action('players', self.showplayers, 'display all online players.')
        self.register_action('groups', self.showgroups, 'display all groups on server (no more than 30).')
        self.register_action('send', self.sendmsgtouser)
        self.register_action('ginfo', self.groupinfo,
                             ' args[gid] show gid info. If gid is None, show the info of the group you joined.')
        self.register_action('ready', self.ready,
                             "Update your status to 'ready' if you are in a group. Undo ready if you are ready.")
        self.refresh()

    def __call__(self):
        print('Type [help] for more instructions...')
        t = 1 / self.fps
        while True:
            if isDead():
                return -1
            time.sleep(t)
            # info = input()
            info = event.event.get()  # event线程接收标准输入的指令
            if info:
                try:
                    super(Lobby, self).__call__(info)
                except ValueError as e:
                    print(str(e))
                    # print('Type [help] for more instructions...')
                except Exception as e:
                    print(str(e))
                    return -1

            msg = active_msg_reciever.read()
            if msg is not None:
                if msg == "close":
                    return -1
                if msg.startswith('gstart'):
                    self.game()
                else:
                    print(msg)

    def showlobbyhelp(self, *args):
        print(self.all_actions())
        '''print('[join] [group no.] to join a group. If gid is out of range, that means quit current group.')
        print('[send] [user ID or user name] to send a message.')
        print('[refresh] to refresh the lobby, show all players and groups.')
        print('[exit] to disconnect the server.')
        print('[players] to display all online players.')
        print('[groups] to display all groups on server (no more than 30).')
        print('[ginfo] [gid] show gid info. If gid is None, show the info of the group you joined.')
        print("[ready] Update your status to 'ready' if you are in a group. Undo ready if you are ready.")'''

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
            raise RuntimeError('ginfo get none from server.')
        if len(msglist) == 0:
            raise ValueError("You haven't joined any group yet.")
        self._showginfo(msglist)

    def ready(self, *args):
        # msglist = getmsgall(self.socket, 'ready')
        write(self.socket, 'ready')
        ClearCLI()
        self.groupinfo()

    def game(self, *args):
        print('start game....')
        time.sleep(1)
        board = Board([])  # 改成服务器发来游戏类型
        # print('Game actions:')
        # print(board.all_actions())
        t = 1 / self.fps
        timer = None
        while True:
            if isDead():
                return
            time.sleep(t)
            info = event.event.get()  # event线程接收标准输入的指令
            if info:
                if info.startswith('quit'):
                    write(self.socket, 'game quit')  # 如果不是自己回合quit，服务器会刷新计时器*****待解决
                    print('Quit the game...')
                    return
                if info.startswith('help'):
                    print(board.all_actions())
                elif timer is not None:  # game action
                    if time.time() - timer < 60:
                        # if board.try_action(info):  # 本地能action server应该也能，总之最终标准在server
                        try:
                            board(self.username + ' ' + info)
                            write(self.socket, 'game ' + info)
                            timer = None
                        except ValueError as e:
                            print(str(e))
                        except Exception as e:
                            print(str(e))
                            return
                    else:
                        timer = None  # 超时

            msg = active_msg_reciever.read()
            if msg is None:
                continue

            if msg.startswith('board'):
                try:
                    board.update_board(msg[5:])
                except:
                    print(f'update_board error, json:\n {msg[5:]}')
                    return
                board.show()
            elif msg.startswith('action'):  # 后面加上限制时间
                print("It's your turn. Action or help.")
                timer = time.time()
                continue
            elif msg.startswith('gend'):
                print(msg[4:].strip())
                return
            else:
                # print('Unknown msg:')
                print(msg)

    def _showginfo(self, msglist):
        gid = msglist.pop()
        print('+' + '-' * (self.width - 2) + '+')
        print(f'| Group [{gid}] Information'.ljust(self.width - 1) + '|')
        print('+' + '-' * (self.width - 2) + '+')
        iterprint(msglist, self.width, idx=True)
        print('+' + '-' * (self.width - 2) + '+')

    def joingroup(self, *args):
        if len(args) == 0:
            raise ValueError('There is no group number behind [join].')
        # server 一个group -> 一个board -> 多个user
        try:
            gid = int(args[0])
        except:
            raise ValueError('Table id should be a number.')
        write(self.socket, f"join {gid}")
        msg = read()
        if msg == 'close':
            raise RuntimeError("Quit server.")
        self.refresh()
        self.groupinfo()
        print(msg)

    def refresh(self, *args):
        ClearCLI()
        self.showplayers()
        self.showgroups()

    def showplayers(self, *args):
        playerlist = getmsgall(self.socket, 'pStat')
        if playerlist is None:
            raise RuntimeError('ginfo get none from server.')
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

    def showgroups(self, *args):
        groups = getmsgall(self.socket, 'gStat')
        if groups is None:
            raise RuntimeError('ginfo get none from server.')
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
        write(self.socket, "exit")
        raise RuntimeError("")

    def sendmsgtouser(self, *args):
        print('[send] has not been implemented.')
