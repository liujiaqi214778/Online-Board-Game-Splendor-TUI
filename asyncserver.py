# 2022/5/3  20:56  liujiaqi
"""
This file is a part of My-Board-Game application.
To run the online server, run this script.


IMPORTANT NOTE:
    server.py needs atleast Python v3.7 to work.
"""
import asyncio
import sys
import threading
import time

from server.log import log, LOG, logThread
from server.asyncreceiver import AsyncReceiver
from server.manager import ServerManager
from utils.socketutils import AsyncReader, AsyncWriter, getIp

# These are constants that can be modified by users. Default settings
# are given. Do not change if you do not know what you are doing.
IPV6 = False

# Define other constants
VERSION = "v2.0"
PORT = 26104


# Initialise a few global variables
glbManager = ServerManager()


# This is a Thread that runs in background to collect user input commands
def adminThread():
    global glbManager
    glbManager.help()
    while True:
        msg = input().strip()
        log(msg, adminput=True)
        glbManager(msg)
        '''try:
            glbManager(msg)
        except Exception as e:
            log(str(e))'''


async def handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global glbManager
    writer = AsyncWriter(writer)
    reader = AsyncReader(reader)
    name = None
    log("New client is attempting to connect.")
    glbManager.total += 1
    try:
        msg = await reader.read()
        log(msg)
        if msg != "PyGame":
            log("Client sent invalid header, closing connection.")
            await writer.awrite("errVer")
        else:
            msg = await reader.read()
            if msg != VERSION:
                log("Client sent invalid header, closing connection.")
                await writer.awrite("errVer")
            elif glbManager.players.isfull():
                log("Server is busy, closing new connections.")
                await writer.awrite("errBusy")
            elif glbManager.is_locked():
                log("SERVER: Server is locked, closing connection.")
                await writer.awrite("errLock")
            else:
                name = await reader.read()
                if not glbManager.push(name, writer):  # test
                    log(f"Client sent invalid user name ({name}), closing connection.")
                    await writer.awrite("errName")
                else:
                    glbManager.totalsuccess += 1
                    log(f"Connection Successful, user name - {name}")

                    await writer.awrite("succ")
                    await AsyncReceiver(reader, writer, name, glbManager)()
                    # await asyncio.to_thread(write_forever, writer)
                    # threading.Thread(target=write_forever, args=(writer,)).start()
                    """while True:
                        msg = await reader.read()
                        if msg == 'exit' or msg == 'quit':
                            break
                        log(f": {msg}", name)
                        await writer.awrite("next")"""

                    await writer.awrite("close")
                    log(f"Player {name} has Quit")
        # await asyncio.sleep(3)
        # close会导致client的 sock.recv()返回一个空byte b''
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
    ipaddr = getIp(public=False)
    if ipaddr == "127.0.0.1":
        log("This machine does not appear to be connected to a network.")
        log("With this limitation, you can only serve the clients ")
        log("who are on THIS machine. Use IP address 127.0.0.1\n")

    else:
        log(f"This machine has a local IP address - {ipaddr}")
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
