import asyncio
import cProfile
from time import time
from random import choice

import config
from panos import network
from minecraft.networking.connection import Connection


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def scan(addresses):
    statuses = []
    for chunk in chunks(addresses, 10000):
        print(f'Scanning {chunk[0][0]}:{chunk[0][1]} to {chunk[-1][0]}:{chunk[-1][1]}')
        start = time()
        statuses += [status for status in
                     await asyncio.gather(*[network.status(ip, port) for ip, port in chunk], return_exceptions=True)
                     if status]
        print(time() - start)
        print(statuses)
    return statuses


ip = '194.125.251.223'
server_location = ('194.125.251.223', 53840)
addresses = [(ip, port) for port in config.PORT_RANGE]
assert server_location in addresses

asyncio.run(scan([server_location]), debug=True)
asyncio.run(scan(addresses), debug=True)
