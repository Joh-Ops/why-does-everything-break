from asyncio.exceptions import TimeoutError

async def get_cracked(uuid, name, session):
   try:
       async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{name}') as resp:
           try:
               json_resp = await resp.json()
               return json_resp['id'] != uuid.replace('-', '')
           except Exception as e:
               return True

   except TimeoutError:
       return True
