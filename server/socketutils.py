# 2022/5/12  0:26  liujiaqi


# Used instead of sock.recv(), because it returns the decoded message, handles
# TCP packet loss, timeout and other useful stuff
def read(sock, timeout=None):
    try:
        sock.settimeout(timeout)
        msg = sock.recv(4096).decode("utf-8").strip()

    except:
        msg = "quit"

    if msg:
        return msg
    return "quit"


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
