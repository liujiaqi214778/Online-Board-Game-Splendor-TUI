# 2022/5/3  19:30  liujiaqi
from board import Board, Player
import threading

# from chess.onlinelib import *
from game import *
from sockutils import *
from lobby import Lobby

VERSION = "v1.0"
PORT = 26103
ERR = (
        "Attempting to connect to server..",
        "[ERR 1] Couldn't find the server..",
        "[ERR 2] Versions are incompatible..",
        "[ERR 3] Server is full (max = 10)..",
        "[ERR 4] The server is locked...",
        "[ERR 5] invalid user name (length > 15 or already exist)...",
        "[ERR 6] Unknown error occured...",
        "You got disconnected from server..",
    )


def main(addr, uname, ipv6=False):
    print("Attempting to connect to server..")
    if ipv6:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        servaddr = (addr, PORT, 0, 0)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servaddr = (addr, PORT)

    try:
        sock.connect(servaddr)
    except:
        print(ERR[1])
        return -1

    thread = threading.Thread(target=bgThread, args=(sock,))
    thread.start()
    write(sock, "PyGame")
    write(sock, VERSION)
    write(sock, uname)

    ret = 1
    msg = read()
    if msg == "errVer":
        print(ERR[2])

    elif msg == "errBusy":
        print(ERR[3])

    elif msg == "errLock":
        print(ERR[4])

    elif msg == "errName":
        print(ERR[5])

    elif msg.startswith("succ"):
        ret = Lobby(sock, uname)()

    else:
        print(msg)
        print(ERR[-1])

    write(sock, "quit")
    sock.close()
    thread.join()
    flush()

    if ret < 0:
        print(ERR[-1])
        return 1
    return ret


if __name__ == '__main__':
    ip = input("Please enter the server ip address: ")
    name = input("Please enter your username: ")
    main(ip, name)

