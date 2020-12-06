import json
import socket
import struct
import asyncio

async def ping(host_string):
    loop = asyncio.get_event_loop()
    async def read_var_int():
        i = 0
        j = 0
        while True:
            k = await loop.sock_recv(sock, 1)
            if not k:
                return 0
            k = k[0]
            i |= (k & 0x7f) << (j * 7)
            j += 1
            if j > 5:
                raise ValueError('var_int too big')
            if not (k & 0x80):
                return i

    ip, port = host_string.split(':')
    port = int(port)
    sock = socket.socket()
    sock.settimeout(0)
    try:
        await loop.sock_connect(sock, (ip, port))

        host = ip.encode('utf-8')
        data = b''
        data += b'\x00'
        data += b'\x04'
        data += struct.pack('>b', len(host)) + host
        data += struct.pack('>H', port)
        data += b'\x01'
        data = struct.pack('>b', len(data)) + data
        await loop.sock_sendall(sock, data + b'\x01\x00')
        length = await read_var_int()
        if length < 10:
            if length < 0:
                raise ValueError('negative length read')
            else:
                raise ValueError(f'invalid response sock.read({length})')

        await loop.sock_recv(sock, 1)
        length = await read_var_int()
        data = b''
        while len(data) != length:
            chunk = await loop.sock_recv(sock, length - len(data))
            if not chunk:
                raise ValueError('connection aborted')
            data += chunk
    finally:
        sock.close()

    return json.loads(data)
