import traceback
from minecraft.exceptions import LoginDisconnect
from minecraft.networking.connection import Connection


def cracked(address, port):
    connection = Connection(address, port, username='test')
    try:
        connection.connect()
    except LoginDisconnect or ConnectionRefusedError:
        return False
    except:
        traceback.print_exc()
    else:
        connection.disconnect()
        return True

def status(address, port):
    try:
        response = Connection(address, port).status()
        status = response
        status['players'] = [player['name'] for player in response['players']['sample']]
        status['max_players'] = response['players']['max']
        status['online'] = response['players']['online']
        return status

    except:
        return None

