import aiohttp
from time import time
from random import choice

import config
from panos.pinger import ping_servers
from panos.hosts_generation import generate_hosts


async def scan_random_aternos(times=1, silent=False, filtering=None):
    ips = [choice(config.IPS) for j in range(int(times))]
    print(f'Scanning {", ".join(ips)}')
    hosts = []
    for ip in ips:
        hosts += generate_hosts(ip, config.PORT_RANGE)
    results = await ping_servers(hosts, silent=silent, filtering=filtering)
    if not results:
        return ['No results.']
    return results


async def scan_full_aternos(silent=False, filtering=None):
    print('Starting full scan...')
    output = []
    async with aiohttp.ClientSession() as session:
        ips = enumerate(config.IPS)
        
        for counter, ip in ips:
            hosts = generate_hosts(ip, config.PORT_RANGE)
            start = time()
            results = await ping_servers(hosts, silent=silent, filtering=filtering, session=session)
            output += results

            print(f'Scanned {counter+1} out of {len(config.IPS)} with {len(results)} results in {time()-start} seconds')
        
    if not output:
        return ['No results.']
    return output


async def scan_specific_aternos(ip, silent=False, filtering=None):
    print('Starting specific scan...')
    hosts = generate_hosts(ip, config.PORT_RANGE)
    results = await ping_servers(hosts, silent=silent, filtering=filtering)
    if not results:
        return ['No results.']
    return results
