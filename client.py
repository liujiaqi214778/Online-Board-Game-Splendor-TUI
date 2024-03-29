# 2022/6/14  10:48  liujiaqi
import threading
import socket
from client.lobby import Lobby
from client.sockutils import read, write, bgThread, flush
from utils.event import event

VERSION = "v2.0"
PORT = 26104
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
    # print(msg)
    if msg == "errVer":
        print(ERR[2])

    elif msg == "errBusy":
        print(ERR[3])

    elif msg == "errLock":
        print(ERR[4])

    elif msg == "errName":
        print(ERR[5])

    elif msg.startswith("succ"):
        event.start()
        ret = Lobby(sock, uname)()
        """while True:
            msg = input("input: ")
            write(sock, msg)
            if msg == 'exit' or msg == 'quit':
                break
            msg = read()
            print(f"read: {msg}")"""
        event.end()

    else:
        print(msg)
        print(ERR[-1])

    write(sock, "exit")
    sock.close()
    thread.join()
    flush()

    if ret < 0:
        print(ERR[-1])
        return 1
    return ret


if __name__ == '__main__':
    # ip = input("Please enter the server ip address: ")
    name = input("Please enter your username: ").strip()
    if ' ' in name:
        name = name.replace(' ', '_')
    ip = '192.168.31.58'
    # ip = '172.30.130.36'
    main(ip, name)
