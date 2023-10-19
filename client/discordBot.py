#for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#for wakeonlan lol
import wakeonlan

#for updating player count
import mcstatus

#for discord api
import discord
from discord.ext import commands

#for talking with the server with minecraft
import websockets
from websockets.sync.client import connect
import asyncio
import json

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents)

async def updatePlayerCount(client):
    while True:
        players = mcstatus.JavaServer.lookup("localhost:25565").status().players.online
        if players == 0:
            await client.change_presence(activity=discord.Game(name="Server is online!"))
        else:
            await client.change_presence(activity=discord.Game(name=f"{players} player online"))
        await asyncio.sleep(60)

@client.event
async def on_ready():
    # await client.tree.sync()
    print("Bot is online")

@client.command()
async def ping(ctx):
    await ctx.channel.send("pong")

# @client.tree.command(name="start", description="Start the Minecraft Server")
@client.command()
async def start(ctx):

    message = await ctx.channel.send("Trying to start the Server")
    await client.change_presence(activity=discord.Game(name="Starting Server"), status=discord.Status.dnd)

    #havent tested if this works
    #for testing the bottom part i now just start
    #the server manually after some time
    wakeonlan.send_magic_packet(os.environ.get("SERVER_MAC"))

    attempts = 0
    while True:
        try:
            if attempts >= 6:
                await message.edit(content="Unable to start the server, contact the admin")
                await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle) 
                return

            connect("ws://localhost:8000")
            break
        except WindowsError:
            attempts+=1
            await message.edit(content=f"Trying to connect. Attempt: {attempts}")
            await asyncio.sleep(10)
   
    await message.edit(content="Server has Started!")
    await client.change_presence(activity=discord.Game(name="Server online"), status=discord.Status.online)

    global  refreshPlayerCount 
    refreshPlayerCount = asyncio.create_task(updatePlayerCount(client))

# @client.tree.command(name="stop", description="Stop the Minecraft Server and Back it up")
@client.command()
async def stop(ctx):
    refreshPlayerCount.cancel()

    message = await ctx.channel.send("Starting the Stopping Process!")
    await asyncio.sleep(1)

    # call the websocket on the pc with the minecraft server running on it to close and back it up.
    # the webserver should responed upon completion with some code to tell the discord bot to change presence to not online or sum
    try:
        websocket = connect("ws://localhost:8000")
    except WindowsError as e:
        await message.edit(content="Unable to Access Server. Might already be offline") 
        return

    websocket.send(json.dumps({"type": "stop"}))
    while True:
        try:
            data = json.loads(websocket.recv())
        except websockets.exceptions.ConnectionClosed:
            await message.edit(content="Something went wrong, please try later or inform the admin")
            return

        if data["status"] == -1:
            await message.edit(content=data["message"]) 
            return

        if data["status"] == 0:
            await client.change_presence(activity=discord.Game(name=data["message"]), status=discord.Status.dnd)
            await message.edit(content=data["message"])

        if data["status"] == 1:
            await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle)
            await message.edit(content=data["message"])
            return

# this commant should somehow be resticted to the person hosting the server as it leaks ips
# add some kind of value to the .env to check for that
@client.command()
async def console(ctx):
    pass

    try:
        websocket = connect("ws://localhost:8000")
    except WindowsError as e:
        await ctx.channel.send(content="Unable to Access Server. Might already be offline") 
        return
    websocket.send(json.dumps({"type": "console"})) 

    while True:
        try:
            data = json.loads(websocket.recv())
        except websockets.exceptions.ConnectionClosed:
            await ctx.channel.send("Something went wrong, please try later or inform the admin")
            return

        if data["status"] == 1:
            finalMessage = "Logs: ```"
            for message in data["logs"]:
                finalMessage += message

            finalMessage += "\n```"
            await ctx.channel.send(finalMessage)
            break

client.run(os.environ.get("DISCORD_BOT_TOKEN"))
