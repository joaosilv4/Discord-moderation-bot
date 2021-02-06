# Core.py
# The core cog. Contains all core functions
# (C) João Silva

# Import required libraries
import random
import sys
import json
import discord
from discord.ext import commands


#
# Class: Core
# This file is used for any core functions and commands
# that exist in the bot to be functional
#
class Core(commands.Cog):
    # Initialize the Class and bot variable
    def __init__(self, bot):
        self.bot = bot

    # Runs this when the cog is ready
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog "Core" is ready')

    # Check if message starts with hi, hello or hey
    # Respond by saying hello to the user
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        listOfWords = ["hi", "hello", "hey"]
        msgcontent = message.content.lower()
        for word in listOfWords:
            if msgcontent.startswith(word):
                await message.channel.send(word.capitalize() + ' ' + message.author.name)
                break

#--------------------------------------------------------------------------------               
                
    # Ping command
    # Used for testing the latency of the bot and whether it is working
    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! {latency}ms')
        
#--------------------------------------------------------------------------------

# Setup function required by discord.py
def setup(bot):
    bot.add_cog(Core(bot))
