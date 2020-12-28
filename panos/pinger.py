import aiohttp
import asyncio
import warnings

import config
from panos.protocol import ping
from panos.filters import filter_result

warnings.filterwarnings("ignore", category=DeprecationWarning)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def is_minecraft(host, session, silent=False, filtering=None):
    try:
        result = await asyncio.wait_for(ping(host), timeout=25)
    except asyncio.exceptions.TimeoutError:
        return None
        
    if filtering and result:
        result = await filter_result(result, filtering, session)
    if not silent:
        print(f'Finished scan on {host}.')
    return result


async def ping_servers(hosts, silent=False, filtering=None, session=None):
    results = []
    if not session:
        async with aiohttp.ClientSession() as session:
            for hostchunk in chunks(hosts, config.CHUNK_SIZE):
                results += await asyncio.gather(
                    *[is_minecraft(host, session, silent=silent, filtering=filtering) for host in hostchunk])

    else:
        for hostchunk in chunks(hosts, config.CHUNK_SIZE):
            results += await asyncio.gather(
                *[is_minecraft(host, session, silent=silent, filtering=filtering) for host in hostchunk])

    return [result for result in results if result]
