from time import sleep
from subprocess import Popen 

#for .env file 
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

#for discord api
import discord
from discord.ext import commands

#for talking with the server with minecraft
from websockets.sync.client import connect
import asyncio
import json

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents, activity=discord.Game(name="Bot Online"), status=discord.Status.idle)

@client.event
async def on_ready():
    print("Bot is online")
    await client.tree.sync()

@client.tree.command(name="start", description="Start the Minecraft Server")
async def start(ctx):

    # localhost will have to be replaced with the static address of the minecraft server or sum
    with connect("ws://localhost:8000") as websocket:
        websocket.send(json.dumps({"type": "status"}))
        message = websocket.recv()

        if message:
            print("on")
        else:
            print("off")

    #check if the server is already running

    await ctx.response.send_message("Starting the Minecraft Server")

    # start wake on lan protocol to start
    # pc with the minecraft server on it
    await client.change_presence(activity=discord.Game(name="Starting Server"), status=discord.Status.idle)

    #check through pings if the server has started
    await client.change_presence(activity=discord.Game(name="Server is online"), status=discord.Status.online)
    


@client.tree.command(name="stop", description="Stop the Minecraft Server and Back it up")
async def stop(ctx):
    await client.change_presence(activity=discord.Game(name="Stoping the Server"), status=discord.Status.dnd) 

    # call the websocket on the pc with the minecraft server running on it to close and back it up.
    # the webserver should responed upon completion with some code to tell the discord bot to change presence to not online or sum
    with connect("ws://localhost:8000") as websocket:
        websocket.send(json.dumps({"type": "stop"}))
        message = websocket.recv()
        print(message)

    await ctx.response.send_message("stop")

client.run(os.environ.get("DISCORD_BOT_TOKEN"))
