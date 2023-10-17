# skript that gets autostarted once the pc with the minecraft server
# is online and logged in (there should be no password e.g. no reason to login
# as i dont know how that would work with wake on lan lol)

import websockets
import asyncio

#server that takes request which are triggert by the main.py of the discord bot
