import asyncio
import traceback
from functools import partial

from minecraft.exceptions import LoginDisconnect
from minecraft.networking.packets import clientbound
from minecraft.networking.connection import Connection


def network_exception_handler(e, info):
    if isinstance(e, (LoginDisconnect, ValueError, BrokenPipeError)):
        pass
    else:
        traceback.print_exc()


async def is_cracked(address, port, timeout=15):
    loop = asyncio.get_running_loop()
    result = asyncio.Queue()
    connection = Connection(address, port, username='panos')

    @connection.listener(clientbound.login.DisconnectPacket, early=True)
    def handle_exit(packet):
        asyncio.run_coroutine_threadsafe(result.put(False), loop)

    @connection.listener(clientbound.play.JoinGamePacket)
    def handle_join_game(packet):
        asyncio.run_coroutine_threadsafe(result.put(True), loop)

    connection.register_exception_handler(network_exception_handler)

    try:
        await asyncio.wait_for(
            loop.run_in_executor(None, connection.connect),
            timeout=timeout
        )
    except (ConnectionRefusedError, ConnectionAbortedError, TimeoutError, asyncio.TimeoutError):
        return False

    try:
        result = await asyncio.wait_for(result.get(), timeout=timeout)
    except asyncio.TimeoutError:
        return False

    # Do not write any packets, which would block
    if connection.connected:
        connection.disconnect(immediate=True)
    return result


async def status(address, port, timeout=15):
    #print(f'{address}:{port} started')
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    def add_to_queue(obj):
        asyncio.run_coroutine_threadsafe(queue.put(obj), loop)

    try:
        await asyncio.wait_for(
            loop.run_in_executor(None, partial(Connection(address, port).status, handle_status=add_to_queue)),
            timeout=timeout
        )
    except (ConnectionRefusedError, TimeoutError, asyncio.exceptions.TimeoutError):
        #print(f'{address}:{port} finished')
        return None
    try:
        response = await asyncio.wait_for(queue.get(), timeout=timeout)
    except asyncio.TimeoutError:
        #print(f'{address}:{port} finished')
        return None

    if not response:
        #print(f'{address}:{port} finished')
        return None

    result = response
    result['max_players'] = response['players']['max']
    result['online'] = response['players']['online']
    if response['players'].get('sample'):
        result['players'] = [player['name'] for player in response['players']['sample']]
    else:
        result['players'] = []
    #print(f'{address}:{port} finished')
    return result
