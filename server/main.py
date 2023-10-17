# skript that gets autostarted once the pc with the minecraft server
# is online and logged in (there should be no password e.g. no reason to login
# as i dont know how that would work with wake on lan lol)

import websockets
import asyncio
import json

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "start":
            continue

        if data["type"] == "stop":
            await websocket.send("hi") 

            
            continue


async def main():
    async with websockets.serve(handler, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
