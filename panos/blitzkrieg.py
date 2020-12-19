import json
import threading
from time import sleep
from queue import Queue
from random import choice, random
import traceback

from panos import network
from minecraft.networking.connection import Connection
from minecraft.networking.packets import Packet, clientbound, serverbound


def random_caps(string):
    return ''.join(choice((str.upper, str.lower))(c) for c in string)


def doom_bot(address, port):
    queue = Queue()
    packet = serverbound.play.ChatPacket()
    packet.message = 'IMPENDING DOOM'

    def handle_evicted(packet):
        queue.put('evicted')

    def handle_disconnected(e, info):
        queue.put('disconnected')
        traceback.print_exception(*info)

    def handle_chat(packet):
        sender = json.loads(packet.json_data)['with'][0]['text']
        if sender[0] == ' ':
            queue.put('disconnected')

    while True:
        connection = Connection(address, port, username=random_caps('impending doom'))
        connection.register_packet_listener(handle_evicted, clientbound.play.DisconnectPacket, early=True)
        connection.register_packet_listener(handle_chat, clientbound.play.ChatMessagePacket)
        connection.register_exception_handler(handle_disconnected)
        connection.connect()

        while queue.empty():
            connection.write_packet(packet)
            sleep(0.5 + random()/4)

        if queue.get() == 'disconnected':
            break


def impending_doom(address, port, max=3):
    status = network.status(address, port)
    available_slots = status['max_players'] - status['online']
    if max > available_slots:
        max = available_slots

    for j in range(max):
        threading.Thread(target=doom_bot, args=(address, port)).start()

