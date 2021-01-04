import aiohttp
import asyncio

from panos.protocol import ping
from panos.filters import filter_result

import config


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def is_minecraft(host, session, verbose=False, silent=False, filtering=None):
    try:
        result = await asyncio.wait_for(ping(host), timeout=25)
    except asyncio.exceptions.TimeoutError:
        return None
        
    if filtering and result:
        result = await filter_result(result, filtering, session)

    if verbose:
        print(f'Finished scan on {host}.')

    if not silent and result:
        print(result)
    return result


async def ping_servers(hosts, verbose=False, silent=False, filtering=None, session=None):
    results = []
    if not session:
        async with aiohttp.ClientSession() as session:
            for hostchunk in chunks(hosts, config.CHUNK_SIZE):
                results += await asyncio.gather(
                    *[is_minecraft(host, session, verbose=verbose, silent=silent, filtering=filtering) for host in hostchunk]
                )

    else:
        for hostchunk in chunks(hosts, config.CHUNK_SIZE):
            results += await asyncio.gather(
                *[is_minecraft(host, session, verbose=verbose, silent=silent, filtering=filtering) for host in hostchunk]
            )

    return [result for result in results if result]
