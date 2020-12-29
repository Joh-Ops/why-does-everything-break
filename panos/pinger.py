import aiohttp
import asyncio

from panos.protocol import ping
from panos.filters import filter_result

import config


async def task_master(task_queue, hosts, master_completed):
    for host in hosts:
        await task_queue.put(host)
    master_completed.set()


async def minecraft_worker(task_queue, out_queue, session, silent, filtering):
    while True:
        host = await task_queue.get()

        try:
            result = await asyncio.wait_for(ping(host), timeout=20)
        except asyncio.exceptions.TimeoutError:
            pass

        else:
            if filtering:
                result = await filter_result(result, filtering, session)
            if result:
                out_queue.put_nowait(result)

        finally:
            if not silent:
                print(f'Finished scan on {host}.')
            task_queue.task_done()


async def ping_servers(hosts, silent=False, filtering=None, session=None):
    task_queue = asyncio.Queue(maxsize=config.MAX_WORKERS)
    out_queue = asyncio.Queue()
    master_completed = asyncio.Event()

    if not session:
        session = aiohttp.ClientSession()
        close_session = True
    else:
        close_session = False

    tasks = [asyncio.create_task(task_master(task_queue, hosts, master_completed))]
    for _ in range(config.MAX_WORKERS):
        tasks.append(asyncio.create_task(
            minecraft_worker(task_queue, out_queue, session, silent, filtering)
        ))


    # Wait for tasks to finish
    await master_completed.wait()
    await task_queue.join()

    for task in tasks:
        task.cancel()
    # Wait for tasks to be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)

    if close_session:
        await session.close()
    return list(out_queue._queue)
