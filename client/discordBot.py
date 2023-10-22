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

async def updatePlayerCount():
    while True:
        try:
            players = mcstatus.JavaServer.lookup(os.environ.get("SERVER_HOSTNAME")+":25565").status().players.online
        except:
            await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle)
            break 

        if players == 0:
            await client.change_presence(activity=discord.Game(name="Server is online!"))
        else:
            await client.change_presence(activity=discord.Game(name=f"{players} player online"))
        await asyncio.sleep(60)

@client.event
async def on_ready():
    try:
        connect("ws://"+os.environ.get("SERVER_HOSTNAME")+":8000")
        global refreshPlayerCount
        refreshPlayerCount = asyncio.create_task(updatePlayerCount())
    except WindowsError:
        await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle)

    print("Bot is online")

@client.command()
async def ping(ctx):
    await ctx.channel.send("pong")

# @client.tree.command(name="start", description="Start the Minecraft Server")
@client.command()
async def start(ctx):

    text = "```Attempting to Start the Server```"
    message = await ctx.channel.send(text)
    await client.change_presence(activity=discord.Game(name="Starting Server"), status=discord.Status.dnd)

    #havent tested if this works
    #for testing the bottom part i now just start
    #the server manually after some time
    wakeonlan.send_magic_packet(os.environ.get("SERVER_MAC"))

    attempts = 0
    while True:
        try:
            if attempts >= 6:
                text += "```Unable to start the server, contact the admin```"
                await message.edit(content=text)
                await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle) 
                return

            connect("ws://"+os.environ.get("SERVER_HOSTNAME")+":8000")
            break
        except WindowsError:
            attempts+=1

            temp = text 
            temp += f"```Trying to connect. Attempt: {attempts}```"
            await message.edit(content=temp)

            await asyncio.sleep(10)
   
    text += "```Server has started```"
    await message.edit(content=text)

    global  refreshPlayerCount 
    refreshPlayerCount = asyncio.create_task(updatePlayerCount())

# @client.tree.command(name="stop", description="Stop the Minecraft Server and Back it up")
@client.command()
async def stop(ctx):
    refreshPlayerCount.cancel()

    text = "```Attempting to stop the server```"
    message = await ctx.channel.send(text)
    await asyncio.sleep(1)

    # call the websocket on the pc with the minecraft server running on it to close and back it up.
    # the webserver should responed upon completion with some code to tell the discord bot to change presence to not online or sum
    try:
        websocket = connect("ws://"+os.environ.get("SERVER_HOSTNAME")+":8000")
    except WindowsError as e:
        text += "```Unable to start the server, contact the admin```"
        await message.edit(content=text)
        return

    websocket.send(json.dumps({"type": "stop"}))
    while True:
        try:
            data = json.loads(websocket.recv())
        except websockets.exceptions.ConnectionClosed:

            text += "```Something went wrong, please try later or inform the admin```"
            await message.edit(content=text)
            return

        if data["status"] == -1:
            text += "```"+data["message"]+"```"
            await message.edit(content=text) 
            return

        if data["status"] == 0:
            await client.change_presence(activity=discord.Game(name=data["message"]), status=discord.Status.dnd)
            text += "```"+data["message"]+"```"
            await message.edit(content=text) 

        if data["status"] == 1:
            await client.change_presence(activity=discord.Game(name="Server is offline"), status=discord.Status.idle)
            text += "```"+data["message"]+"```"
            await message.edit(content=text) 
            return

# this commant should somehow be resticted to the person hosting the server as it leaks ips
# add some kind of value to the .env to check for that
@client.command()
async def console(ctx):
    try:
        websocket = connect("ws://"+os.environ.get("SERVER_HOSTNAME")+":8000")
    except WindowsError as e:
        await ctx.channel.send("```Unable to start the server, contact the admin```")
        return
    websocket.send(json.dumps({"type": "console"})) 

    while True:
        try:
            data = json.loads(websocket.recv())
        except websockets.exceptions.ConnectionClosed:
            await ctx.channel.send("```Something went wrong, please try later or inform the admin```")
            return

        if data["status"] == 1:
            finalMessage = "Logs: ```"
            for message in data["logs"]:
                finalMessage += message

            finalMessage += "\n```"
            await ctx.channel.send(finalMessage)
            break

client.run(os.environ.get("DISCORD_BOT_TOKEN"))
