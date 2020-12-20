import asyncio
import traceback
from time import sleep
from random import choice

from panos import network
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound


#TODO: fix mysterious bug that breaks impending doom when I have 3 or more of them sending messages at the same time

def random_caps(string):
    return ''.join(choice((str.upper, str.lower))(c) for c in string)


class DoomConnection:
    def __init__(self, address, port):
        self.port = port
        self.address = address

        self._connection = Connection(self.address, self.port, username=random_caps('impending doom'))
        self._connection.register_packet_listener(self.handle_evicted, clientbound.play.DisconnectPacket, early=True)
        self._connection.register_exception_handler(self.handle_error)
        self._connection.connect()

    def handle_evicted(self, packet):
        self._connection = Connection(self.address, self.port, username=random_caps('impending doom'))
        self._connection.register_packet_listener(self.handle_evicted, clientbound.play.DisconnectPacket, early=True)
        self._connection.register_exception_handler(self.handle_error)
        self._connection.connect()

    def __getattr__(self, instance, owner=None):
        return getattr(self._connection, instance)


async def impending_doom(address, port, max=3, time=10):
    connections = [DoomConnection(address, port) for j in range(max)]
    await asyncio.sleep(time)
    for connection in connections:
        connection.disconnect(immediate=True)
