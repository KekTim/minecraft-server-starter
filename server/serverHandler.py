# Skript gets autostarted when starting the PC over LAN
# the PC should have no password so it instantly gets logged in

# for the websocket
import websockets
import asyncio
import json

# for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# for the backup
import shutil
import datetime

# to check how many players are online 
from mcstatus import JavaServer 

# start the server!
import subprocess

# for logging the minecraft console
import threading


def startMinecraftServer():
    """
    Starts the Server and then returns the process
    """
    server = subprocess.Popen(os.environ.get("SERVER_START_FILE"), cwd=os.environ.get("SERVER_LOCATION"), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, universal_newlines=True)

    while True:
        # make sure windows cmd uses chcp 65001
        line = server.stdout.readline()

        if line != "":
            print(line)

        with open("logs.txt", "a") as file:
            file.write(line)

        # if done the then continue
        if "Done" in line:
            print("Minecraft Server has Started!")
            logThread = threading.Thread(target=logConsole, args=(server,))
            logThread.start()

            return server

        # if server fails to start becauser ressource might already be open somewhere else then shut down
        if "Failed" in line:
            print("Miencraft Server has failed to start. Shutdown")
            os.system("shutdown /s /t 10")

def logConsole(server):
    while True:
        line = server.stdout.readline()
        if line == "":
            continue
        
        with open("logs.txt", "a") as file:
            file.write(line)

def closeMinecraftServer(serverToClose):
    serverToClose.stdin.write("stop\n")
    serverToClose.stdin.flush()
    serverToClose.wait()
    
def backupMinecraftServer():
    serverLocation = os.environ.get("SERVER_LOCATION")
    backupLocation = os.path.join(os.environ.get("BACKUP_LOCATION"), datetime.datetime.now().strftime("Date %d.%m.%Y Time %H.%M.%S"))
    shutil.make_archive(backupLocation, "zip", serverLocation)


server = startMinecraftServer()
stopping = False

async def close(websocket):
    global server
    global stopping

    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "console":
            with open("logs.txt", "r") as file:
                await websocket.send(json.dumps({"status": 1, "logs": file.readlines()[-100:]}))
            await websocket.close()
            continue 

        if data["type"] == "stop":
            if stopping:
                await websocket.send(json.dumps({"status": -1, "message": "Server is already stopping"}))
                await websocket.close()
                print("Server is already stopping")
                continue

            try:
                serverLookup = JavaServer.lookup("localhost:25565").status()
            except:
                await websocket.send(json.dumps({"status": -1, "message": "Minecraft Server seems to be offline but not the PC. Shutting down now."}))
                await websocket.close()
                print("Minecraft Server seems to be offline but not the PC. Shutting down now.")
                os.system("shutdown /s /t 10")
                continue

            if serverLookup.players.online != 0:
                await websocket.send(json.dumps({"status": -1, "message": "Can't shut down with players online"}))
                await websocket.close()
                print("Can't shut down with players online")
                continue

            stopping = True

            await websocket.send(json.dumps({"status": 0, "message": "Starting to closing process"}))
            print("Starting to closing process") 
            closeMinecraftServer(server)
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 0, "message": "Minecraft Server closed successfully. Starting backup process"}))
            print("Minecraft Server closed successfully. Starting backup process") 
            backupMinecraftServer()
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 0, "message": "Backup completed successfully. Starting shutdown"}))
            print("Backup completed successfully. Starting shutdown")
            os.system("shutdown /s /t 10")
            await asyncio.sleep(2)

            await websocket.send(json.dumps({"status": 1, "message": "Shutting down. Bye"}))
            await websocket.close()
            print("Shutting down. Bye")

async def main():
    async with websockets.serve(close, "", 8000): #idk if there neds to be an ip in the ""
        await asyncio.Future()  # run forever

asyncio.run(main())
