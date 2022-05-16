# 2022/5/3  20:56  liujiaqi
"""
This file is a part of My-PyChess application.
To run the online server, run this script.

For more information, see onlinehowto.txt

IMPORTANT NOTE:
    Server.py needs atleast Python v3.6 to work.
"""
import socket
import threading
from server.log import log, LOG, logThread
from server.socketutils import write, read, getIp
from server.reactor import ServerReactor
from server.manager import ServerManager

# These are constants that can be modified by users. Default settings
# are given. Do not change if you do not know what you are doing.
IPV6 = False

# Define other constants
VERSION = "v1.0"
PORT = 26103


# Initialise a few global variables
end = False
lock = False
glbManager = ServerManager()


# This is a Thread that runs in background to remove disconnected people
def kickDisconnectedThread():
    global glbManager
    glbManager.kickdisconnectedplayer()


# This is a Thread that runs in background to collect user input commands
def adminThread():
    global end, lock, glbManager
    while True:
        msg = input().strip()
        log(msg, adminput=True)

        if msg == "report":
            glbManager.report()

        elif msg == "mypublicip":
            log("Determining public IP, please wait....")
            PUBIP = getIp(public=True)
            if PUBIP == "127.0.0.1":
                log("An error occurred while determining IP")

            else:
                log(f"This machine has a public IP address {PUBIP}")

        elif msg == "lock":
            if lock:
                log("Aldready in locked state")
            else:
                lock = True
                log("Locked server, no one can join now.")

        elif msg == "unlock":
            if lock:
                lock = False
                log("Unlocked server, all can join now.")
            else:
                log("Aldready in unlocked state.")

        elif msg.startswith("kick "):
            for k in msg[5:].split():
                glbManager.kick(k)

        elif msg == "kickall":
            glbManager.kickall()

        elif msg == "quit":
            lock = True
            glbManager.kickall()

            log("Exiting application - Bye")
            log(None)

            end = True
            if IPV6:
                with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
                    s.connect(("::1", PORT, 0, 0))
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(("127.0.0.1", PORT))
            return

        else:
            log(f"Invalid command entered ('{msg}').")
            log("See 'onlinehowto.txt' for help on how to use the commands.")


# Does the initial checks and lets players in.
def initPlayerThread(sock):
    global glbManager
    log("New client is attempting to connect.")
    glbManager.total += 1

    if read(sock, 3) != "PyGame":
        log("Client sent invalid header, closing connection.")
        write(sock, "errVer")

    elif read(sock, 3) != VERSION:
        log("Client sent invalid version info, closing connection.")
        write(sock, "errVer")

    elif glbManager.players.isfull():
        log("Server is busy, closing new connections.")
        write(sock, "errBusy")

    elif lock:
        log("SERVER: Server is locked, closing connection.")
        write(sock, "errLock")

    else:
        name = read(sock, 3)
        if not glbManager.push(name, sock):
            log("Client sent invalid user name (length > 15 or none or already exist), closing connection.")
            write(sock, "errName")
        else:
            glbManager.totalsuccess += 1
            # key = genKey()
            log(f"Connection Successful, user name - {name}")

            write(sock, "succ")
            ServerReactor(sock, name, glbManager.players, glbManager.groups)()
            write(sock, "close")
            log(f"Player {name} has Quit")

            try:
                glbManager.clearplayerinfo(name)
            except:
                pass
    sock.close()


# Initialize the main socket
log(f"Welcome to My-game Server, {VERSION}\n")
log("INITIALIZING...")

if IPV6:
    log("IPv6 is enabled. This is NOT the default configuration.")

    mainSock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    mainSock.bind(("::", PORT, 0, 0))
else:
    log("Starting server with IPv4 (default) configuration.")
    mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mainSock.bind(("0.0.0.0", PORT))

    IP = getIp(public=False)
    if IP == "127.0.0.1":
        log("This machine does not appear to be connected to a network.")
        log("With this limitation, you can only serve the clients ")
        log("who are on THIS machine. Use IP address 127.0.0.1\n")

    else:
        log(f"This machine has a local IP address - {IP}")
        log("USE THIS IP IF THE CLIENT IS ON THE SAME NETWORK.")
        log("For more info, read file 'onlinehowto.txt'\n")

mainSock.listen(16)
log("Successfully Started.")
log(f"Accepting connections on port {PORT}\n")

threading.Thread(target=adminThread).start()
threading.Thread(target=kickDisconnectedThread, daemon=True).start()
if LOG:
    log("Logging is enabled. Starting to log all output")
    threading.Thread(target=logThread).start()

while True:
    s, _ = mainSock.accept()
    if end:
        break

    threading.Thread(target=initPlayerThread, args=(s,), daemon=True).start()
mainSock.close()
