# Skript gets autostarted when starting the PC over LAN
# the PC should have no password



#for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#start the server!
import subprocess
subprocess.Popen([os.environ.get("SERVER_START_FILE")], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)


import websockets
import asyncio
import json

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "backup":
            await websocket.send("backuped")
            continue

        # kinda redundaned because only message that can get send is the stop request.
        # expect if i make an extra option to back the server up manually
        if data["type"] == "stop":
            await websocket.send("stopped") 
            continue


async def main():
    async with websockets.serve(handler, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
