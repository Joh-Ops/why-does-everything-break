import asyncio
from time import time
from random import choice

import config
from panos import network


async def scan(addresses):
    statuses = await asyncio.gather(*[network.status(ip, port) for ip, port in addresses])
    return [status for status in statuses if status]


ip = choice(config.IPS)
addresses = [(ip, port) for port in config.PORT_RANGE]

start = time()
statuses = asyncio.run(scan(addresses))
print(time() - start)
