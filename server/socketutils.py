# 2022/5/12  0:26  liujiaqi
import socket
from urllib.request import urlopen


# Used instead of sock.recv(), because it returns the decoded message, handles
# TCP packet loss, timeout and other useful stuff
def read(sock, timeout=None):
    try:
        sock.settimeout(timeout)

        msg = sock.recv(4096).decode("utf-8").strip()

    except:
        msg = "exit"

    if msg:
        return msg
    return "exit"


# A function to message the server, this is used instead of socket.send()
# beacause it buffers the message, handles packet loss and does not raise
# exception if message could not be sent
def write(sock, msg, prefix=False):
    if msg:
        if prefix:
            msg = '@' + msg + '@'
        buffedmsg = msg + (" " * (4096 - len(msg)))
        try:
            sock.sendall(buffedmsg.encode("utf-8"))
        except:
            pass


# A function to get IP address. It can give public IP or private.
def getIp(public):
    if public:
        try:
            ip = urlopen("https://api64.ipify.org").read().decode()
        except:
            ip = "127.0.0.1"

    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
    return ip
