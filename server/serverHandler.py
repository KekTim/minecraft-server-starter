# Skript gets autostarted when starting the PC over LAN
# the PC should have no password


#for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#start the server!
import subprocess

def startMinecraftServer():
    server = subprocess.Popen([os.environ.get("SERVER_START_FILE")], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    while True:

        # some check if this takes like 50 seconds and if yes then stop
        # and maybe restart and keep track of how many restarts happend
        # so when there are 3 consecutive just stop and shut down or sum

        output_line = str(server.stdout.readline().strip())
        if "Done" in output_line:
            print("Minecraft Server has Started!")
            return server
server = startMinecraftServer()


import websockets
import asyncio
import json

async def close(websocket):
    async for message in websocket:
        data = json.loads(message)



async def main():
    async with websockets.serve(close, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
