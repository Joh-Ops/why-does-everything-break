import threading
from time import sleep
from random import choice
from queue import Queue

from panos import network
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound


def random_caps(string):
    return ''.join(choice((str.upper, str.lower))(c) for c in string)


def doom_bot(address, port):
    queue = Queue()

    def handle_evicted(packet):
        queue.put('evicted')
    def handle_disconnected(packet):
        queue.put('disconnected')

    while True:
        connection = Connection(address, port, username=random_caps('impending doom'))
        connection.register_packet_listener(handle_evicted, clientbound.DisconnectPacket, early=True)
        connection.register_exception_handler(handle_disconnected)
        connection.connect()

        while queue.empty():
            sleep(0.05)
        if queue.get() == 'disconnected':
            break


def impending_doom(address, port, max=5):
    status = network.status(address, port)
    print(status)
    available_slots = status['max_players'] - status['online']
    if max > available_slots:
        max = available_slots

    for j in range(max):
        threading.Thread(target=doom_bot, args=(address, port)).start()
