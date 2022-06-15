# 2022/6/15  15:52  liujiaqi
import asyncio
import socket
from urllib.request import urlopen


def encode_msg(msg, msg_type=0):
    # 1 byte type + 3bytes msg_len
    msg_len = len(msg)
    header = msg_type.to_bytes(1, byteorder='big') + msg_len.to_bytes(3, byteorder='big')
    return header + msg.encode("utf-8")


class AsyncWriter:
    def __init__(self, writer: asyncio.StreamWriter):
        self.writer = writer

    def write(self, msg, msg_type=0):
        self.writer.write(encode_msg(msg, msg_type))

    async def awrite(self, msg, msg_type=0):
        self.writer.write(encode_msg(msg, msg_type))
        await self.writer.drain()

    def close(self):
        self.writer.close()

    async def drain(self):
        await self.writer.drain()


class AsyncReader:
    def __init__(self, reader: asyncio.StreamReader):
        self.reader = reader

    async def read(self):
        msg = await self.reader.read(4)  # 4字节消息头
        msg_type = msg[0]
        msg_len = int.from_bytes(msg[1:4], byteorder='big')
        msg = await self.reader.read(msg_len)
        return msg.decode().strip()


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


def read(sock, timeout=None):  # 弃用
    try:
        sock.settimeout(timeout)

        msg = sock.recv(4096).decode("utf-8").strip()

    except:
        msg = "exit"

    if msg:
        return msg
    return "exit"
