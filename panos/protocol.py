import asyncio
import base64
import json
import socket
import struct
import traceback

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Server:
    def __init__(self, host, data):
        self.description = data['description']
        if isinstance(self.description, dict):
            try:
                self.description = self.description['text']
            except:
                self.description = self.description['translate']

        self.host = host
        self.icon = base64.b64decode(data.get('favicon', '')[22:])
        self.players = Players(data['players'])
        self.version = data['version']['name']
        self.protocol = data['version']['protocol']

    def __str__(self):
        return f"{self.host} - {self.players} - {self.version} - \"{self.description}\""

class Players(list):
    def __init__(self, data):
        super().__init__(Player(x) for x in data.get('sample', []))
        self.max = data['max']
        self.online = data['online']

    def __str__(self):
        return f'{self.online}/{self.max}'

class Player:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']

    def __str__(self):
        return f'{self.name} | {self.id}'
        
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

        return Server(host_string, json.loads(data))
    
    except Exception as e:
        #print(traceback.format_exc())
        return None

    finally:
        sock.close()
