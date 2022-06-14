# 2022/5/3  20:56  liujiaqi
"""
This file is a part of My-Board-Game application.
To run the online server, run this script.


IMPORTANT NOTE:
    server.py needs atleast Python v3.7 to work.
"""
import socket
import asyncio
import sys
import threading
import time

from server.log import log, LOG, logThread
from server.socketutils import write, read, getIp
from server.cmdreceiver import CmdReceiver
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

        elif msg == "quit" or msg == 'exit':
            lock = True
            glbManager.kickall()

            log("Exiting application - Bye")
            log(None)

            end = True
            time.sleep(3)
            # 怎么关闭 asyncio.run() ?
            # server.serve_forever() 后怎么cancel???
            sys.exit()

        else:
            log(f"Invalid command entered ('{msg}').")


def encode_msg(msg: str):
    return msg.encode("utf-8")


async def handle_echo(reader, writer):
    global glbManager
    name = None
    log("New client is attempting to connect.")
    glbManager.total += 1
    try:
        data = await reader.readline()
        msg = data.decode()[:-1]
        log(msg)
        if msg != "PyGame":
            log("Client sent invalid header, closing connection.")
            writer.write(encode_msg("errVer"))
        else:
            data = await reader.readline()
            msg = data.decode()[:-1]
            if msg != VERSION:
                log("Client sent invalid header, closing connection.")
                writer.write(encode_msg("errVer"))
            elif glbManager.players.isfull():
                log("Server is busy, closing new connections.")
                writer.write(encode_msg("errBusy"))
            elif lock:
                log("SERVER: Server is locked, closing connection.")
                writer.write(encode_msg("errLock"))
            else:
                data = await reader.readline()
                name = data.decode()[:-1]
                if not glbManager.push(name, 'sock'):  # test
                    log(f"Client sent invalid user name ({name}), closing connection.")
                    writer.write(encode_msg("errName"))
                else:
                    glbManager.totalsuccess += 1
                    # key = genKey()
                    log(f"Connection Successful, user name - {name}")

                    writer.write(encode_msg("succ"))
                    # CmdReceiver(sock, name, glbManager)()
                    while True:
                        data = await reader.readline()
                        msg = data.decode()[:-1]
                        if msg == 'exit' or msg == 'quit':
                            break
                        log(f": {msg}", name)
                        writer.write(encode_msg("next"))
                        await writer.drain()

                    writer.write(encode_msg("close"))
                    log(f"Player {name} has Quit")

                    try:
                        glbManager.clearplayerinfo(name)
                    except:
                        pass
        await writer.drain()
        writer.close()
    except Exception as e:
        log(str(e))
    finally:
        if name is not None:
            log(f"{name} quit server.")
            glbManager.clearplayerinfo(name)

    '''r = asyncio.StreamReader()
    r.readuntil()'''


async def main():
    IP = getIp(public=False)
    if IP == "127.0.0.1":
        log("This machine does not appear to be connected to a network.")
        log("With this limitation, you can only serve the clients ")
        log("who are on THIS machine. Use IP address 127.0.0.1\n")

    else:
        log(f"This machine has a local IP address - {IP}")
        log("USE THIS IP IF THE CLIENT IS ON THE SAME NETWORK.")

    ip = '0.0.0.0'
    if IPV6:
        ip = '::'
    server = await asyncio.start_server(handle_echo, ip, PORT)
    log("Successfully Started.")
    log(f"Accepting connections on port {PORT}\n")

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    # Initialize the main socket
    log(f"Welcome to My-game Server, {VERSION}\n")
    log("INITIALIZING...")

    threading.Thread(target=adminThread).start()

    if LOG:
        log("Logging is enabled. Starting to log all output")
        threading.Thread(target=logThread).start()

    asyncio.run(main())
