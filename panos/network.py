import traceback
from time import sleep
from queue import Queue

from minecraft.exceptions import LoginDisconnect
from minecraft.networking.packets import clientbound
from minecraft.networking.connection import Connection


def network_exception_handler(e, info):
    if isinstance(e, (LoginDisconnect, ConnectionRefusedError, ValueError)):
        pass
    else:
        traceback.print_tb(e)

def is_cracked(address, port):
    result = Queue()
    connection = Connection(address, port, username='panos')

    @connection.listener(clientbound.login.DisconnectPacket, early=True)
    def handle_exit(packet):
        result.put(False)

    @connection.listener(clientbound.play.JoinGamePacket)
    def handle_join_game(packet):
        result.put(True)

    connection.register_exception_handler(network_exception_handler)

    connection.connect()
    while result.empty():
        sleep(0.05)

    is_cracked = result.get()
    if connection.connected:
        connection.disconnect()
    return is_cracked


def status(address, port):
    try:
        response = Connection(address, port).status()
        if not response:
            return None

        status = response
        status['players'] = [player['name'] for player in response['players']['sample']]
        status['max_players'] = response['players']['max']
        status['online'] = response['players']['online']
        return status

    except:
        return None

