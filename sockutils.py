# 2022/5/3  19:43  liujiaqi
'''
This file is a part of My-PyChess application.
In this file, we define a few utility funtions and wrappers for socket related
stuff.
'''
import queue
import socket

q = queue.Queue()
active_msg_q = queue.Queue()  # server 主动发来的消息
isdead = False


# Define a background thread that continuously runs and gets messages from
# server, formats them and puts them into a queue (IO buffer).
def bgThread(sock):
    global isdead
    isdead = False
    while True:
        try:
            msg = sock.recv(128).decode("utf-8").strip()
        except Exception as e:
            print(repr(e))
            break
        if not msg or msg == "close":
            break
        if msg.startswith('@#@'):  # prefix of server's active message
            active_msg_q.put(msg[3:])
        elif msg != "........":
            q.put(msg)
    isdead = True


class ActiveMsgReciever:
    def __init__(self, que):
        self.queue = que

    def read(self):
        try:
            out = self.queue.get_nowait()
        except:
            return None
        return out


active_msg_reciever = ActiveMsgReciever(active_msg_q)

# Returns wether background thread is dead and IO buffer is empty.
def isDead():
    return q.empty() and isdead


# A function to read messages sent from the server, reads from queue.
def read():
    if isDead():
        return "close"
    return q.get()


# Check wether a message is readable or not
def readable():
    if isDead():
        return True
    return not q.empty()


# Flush IO Buffer. Returns False if quit command is encountered. True otherwise.
def flush():
    while readable():
        if read() == "close":
            return False
    return True


# A function to message the server, this is used instead of socket.send()
# beacause it buffers the message, handles packet loss and does not raise
# exception if message could not be sent
def write(sock, msg):
    if msg:
        buffedmsg = msg + (" " * (128 - len(msg)))
        try:
            sock.sendall(buffedmsg.encode("utf-8"))
        except:
            pass


def getmsgall(sock, msg='pStat'):
    if not flush():
        return None

    write(sock, msg)
    msg = read()
    data = []
    if msg.startswith("enum"):
        for i in range(int(msg[4:])):
            newmsg = read()
            if newmsg == "close":
                return None
            else:
                data.append(newmsg)
    elif msg != 'xxx':
        data.append(msg)
    return data
