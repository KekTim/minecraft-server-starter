# Skript gets autostarted when starting the PC over LAN
# the PC should have no password

#for the websocket
import websockets
import asyncio
import json

#for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#for the backup
import shutil
import datetime

#start the server!
import subprocess

def startMinecraftServer():
    server = subprocess.Popen([os.environ.get("SERVER_START_FILE")], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    while True:

        # some check if this takes like 50 seconds and if yes then stop
        # and maybe restart and keep track of how many restarts happend
        # so when there are 3 consecutive just stop and shut down or sum

        output_line = str(server.stdout.readline().strip())
        print(output_line) 
        if "Done" in output_line:
            print("Minecraft Server has Started!")
            return server

def closeMinecraftServer(serverToClose):
    serverToClose.stdin.write(b"stop\n")
    serverToClose.stdin.flush()
    serverToClose.wait()
    
def backupMinecraftServer():
    from werkzeug.utils import secure_filename
    serverLocation = os.environ.get("SERVER_LOCATION")
    backupLocation = os.path.join(os.environ.get("BACKUP_LOCATION"), secure_filename(datetime.datetime.now().strftime("Date %d.%m.%Y Time %H.%M.%S")))
    shutil.make_archive(backupLocation, "zip", serverLocation)


server = startMinecraftServer()
stopping = False
async def close(websocket):
    async for message in websocket:
        data = json.loads(message)

        if data["type"] != "stop":
            websocket.send(json.dumps({"message": "not right type"}))
            websocket.close()
            continue

        if not stopping:
            websocket.send(json.dumps({"message": "already stopping"}))
            websocket.close()
            continue

        stopping = True

        await websocket.send(json.dumps({"message": "closing server"}))
        closeMinecraftServer(server)

        await websocket.send(json.dumps({"message": "server closed and starting backup"}))
        backupMinecraftServer()

        await websocket.send(json.dumps({"message": "backup complete and starting shutdown"}))
        websocket.close()
        
        import sys
        sys.exit()
        # os.system("shutdown /s /t 10")


async def main():
    async with websockets.serve(close, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
