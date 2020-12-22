import aiohttp
from time import time
from itertools import chain

import config
from panos.pinger import ping_servers
from panos.hosts_generation import generate_hosts, randomize_hosts


async def scan_random_aternos(times=1, silent=False, filtering=None):
    print('Starting random scan...')
    hosts = list(chain(*[randomize_hosts(config.IPS, config.PORT_RANGE) for j in range(int(times))]))
    results = await ping_servers(hosts, silent=silent, filtering=filtering)
    if not results:
        return ['No results.']
    return results


async def scan_full_aternos(chunks=1, silent=False, filtering=None):
    print('Starting full scan...')
    output = []
    async with aiohttp.ClientSession() as session:
        ips = enumerate(config.IPS)
        
        for counter, ip in ips:
            old_counter = counter
            hosts = generate_hosts(ip, config.PORT_RANGE)
            try:
                for j in range(int(chunks)-1):
                    counter, ip = next(ips)
                    hosts += generate_hosts(ip, config.PORT_RANGE)
            except StopIteration:
                pass
            
            start = time()
            results = await ping_servers(hosts, silent=silent, filtering=filtering, session=session)
            output += results

            if old_counter == counter:
                print(f'Scanned {counter+1} out of {len(config.IPS)} with {len(results)} results in {time()-start} seconds')
            else:
                print(f'Scanned {old_counter+1}-{counter+1} out of {len(config.IPS)} with {len(results)} results in {time()-start} seconds')
        
    if not output:
        return ['No results.']
    return output


async def scan_specific_aternos(ip, silent=False, filtering=None):
    print('Starting specific scan...')
    hosts = generate_hosts(ip, config.PORTRANGE)
    results = await ping_servers(hosts, silent=silent, filtering=filtering)
    if not results:
        return ['No results.']
    return results
