# 2022/6/14  10:44  liujiaqi
import queue
from utils.socketutils import encode_msg

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
            msg = sock.recv(4)  # 4字节消息头
            # server 中的 writer.close() 会导致这里的recv 收到一个 b''
            if not msg:
                break
            msg_type = msg[0]
            msg_len = int.from_bytes(msg[1:4], byteorder='big')
            if not msg_len:
                continue
            msg = sock.recv(msg_len).decode("utf-8").strip()
            if msg == "close":
                break
            if not msg_type:
                q.put(msg)
            else:
                active_msg_q.put(msg)

        except Exception as e:
            print(repr(e))
            break
    isdead = True


class ActiveMsgReciever:
    def __init__(self, que):
        self.queue = que

    def read(self, timeout=None):
        if timeout is not None:
            out = self.queue.get(timeout=timeout)
        else:
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
        try:
            sock.sendall(encode_msg(msg))
        except:
            pass


def getmsgall(sock, msg='pStat'):  # 即将弃用
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

