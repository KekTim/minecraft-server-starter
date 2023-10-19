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

#mc status
from mcstatus import JavaServer 

#start the server!
import subprocess

import threading

def startMinecraftServer():
    server = subprocess.Popen([os.environ.get("SERVER_START_FILE")], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, universal_newlines=True)
    while True:

        # some check if this takes like 50 seconds and if yes then stop
        # and maybe restart and keep track of how many restarts happend
        # so when there are 3 consecutive just stop and shut down or sum

        line = str(server.stdout.readline().strip())
        print(line) 
        if "Done" in line:
            print("Minecraft Server has Started!")

            logThread = threading.Thread(target=logConsole, args=(server,))
            logThread.start()

            return server

serverLogs = []
def logConsole(server):
    global serverLogs
    while True:

        line = server.stdout.readline()

        if line == "":
            continue

        serverLogs.append(line)
        if len(serverLogs) >= 100:
            serverLogs.pop(0)

def closeMinecraftServer(serverToClose):
    serverToClose.stdin.write("stop\n")
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
    global server
    global stopping

    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "console":
            await websocket.send(json.dumps({"status": 1, "logs": serverLogs}))
            await websocket.close()
            continue 

        if data["type"] == "stop":
            if stopping:
                await websocket.send(json.dumps({"status": -1, "message": "already stopping"}))
                await websocket.close()
                print("already stopping")
                continue

            try:
                serverLookup = JavaServer.lookup("localhost:25565").status()
            except:
                await websocket.send(json.dumps({"status": -1, "message": "server seems to be offline. this should not be possible please contact admin"}))
                await websocket.close()
                print("server seems to be offline. this should not be possible please contact admin")
                continue

            if serverLookup.players.online != 0:
                await websocket.send(json.dumps({"status": -1, "message": "won't stop, there are people playing"}))
                await websocket.close()
                print("won't stop, there are people playing")
                continue

            stopping = True

            await websocket.send(json.dumps({"status": 0, "message": "closing server"}))
            print("closing server") 
            closeMinecraftServer(server)
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 0, "message": "server closed and starting backup"}))
            print("server closed and starting backup") 
            backupMinecraftServer()
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 0, "message": "backup complete and starting shutdown"}))
            print("backup complete and starting shutdown")
            # os.system("shutdown /s /t 10")
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 1, "message": "shutted down"}))
            await websocket.close()
            print("shutted down")

            # server = startMinecraftServer() # so i dont have to restart
            # stopping = False

async def main():
    async with websockets.serve(close, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
