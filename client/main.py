import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix=".", intents=intents, activity=discord.Game(name="Server Live!"), status=discord.Status.idle)

@client.event
async def on_ready():
    print("Bot is online")
    await client.tree.sync()

@client.tree.command(name="start", description="Start the Minecraft Server")
async def start(ctx):

    # start wake on lan protocol to start
    # pc with the minecraft server on it
    await ctx.response.send_message("start")

@client.tree.command(name="stop", description="Stop the Minecraft Server and Back it up")
async def stop(ctx):

    await client.change_presence(activity=discord.Game(name="Stoping the Server"), status=discord.Status.dnd) 

    # call the websocket on the pc with the minecraft server running on it to close and back it up.
    # the webserver should responed upon completion with some code to tell the discord bot to change presence to not online or sum

    

    await ctx.response.send_message("stop")

client.run(os.environ.get("DISCORD_BOT_TOKEN"))
