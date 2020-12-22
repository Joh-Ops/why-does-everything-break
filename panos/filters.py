import asyncio
from panos.api_requests import get_cracked


async def filter_cracked(result, session):
    if any(asyncio.gather(*[get_cracked(player.id, player.name, session) for player in result.players])):
        return result
    else:
        return None             

async def filter_premium(result, session):
    if not any(asyncio.gather(*[get_cracked(player.id, player.name, session) for player in result.players])):
        return result
    else:
        return None             

def filter_version(result, version_filter):
    if version_filter in result.version:
        return result
    else:
        return None

def filter_populated(result):
    if result.players.online > 0:
        return result
    else:
        return None

def filter_empty(result):
    if result.players.online == 0:
        return result
    else:
        return None

async def filter_result(result, filtering, session):
    result_modified = result
    filtering_string = filtering
    if '(cracked)' in filtering_string and result_modified:
        result_modified = await filter_cracked(result_modified, session)
        filtering_string = filtering_string.replace('(cracked)', '')

    if '(premium)' in filtering_string and result_modified:
        result_modified = await filter_premium(result_modified, session)
        filtering_string = filtering_string.replace('(premium)', '')

    if '(populated)' in filtering_string and result_modified:
        result_modified = filter_populated(result_modified)
        filtering_string = filtering_string.replace('(populated)', '')

    if '(empty)' in filtering_string and result_modified:
        result_modified = filter_empty(result_modified)
        filtering_string = filtering_string.replace('(empty)', '')
        
    if filtering_string and result_modified:
        result_modified = filter_version(result_modified, filtering_string)

    return result_modified
