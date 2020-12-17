import traceback
from minecraft.exceptions import LoginDisconnect
from minecraft.networking.connection import Connection
from minecraft.networking.packets import serverbound


def cracked(address, port):
    connection = Connection(address, port, username='panos')
    try:
        connection.connect()
    except LoginDisconnect or ConnectionRefusedError:
        return False
    except:
        traceback.print_exc()
    else:
        connection.disconnect()
        return True

def test():
    print(cracked('127.0.0.1', 25565))
    print('a')

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

