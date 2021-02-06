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

    # Ping command
    # Used for testing the latency of the bot and whether it is working
    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! {latency}ms')

    # Info command
    # Used for displaying information about the bot
    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(title="Information about the Terabyte Bot")
        embed.color = random.randint(0, 0xffffff)
        pythonVersion = str(sys.version).split(" ")
        pythonVersion = pythonVersion[0]
        embed.add_field(name="Python", value=f"[{pythonVersion}](https://www.python.org)")
        embed.add_field(name="Discord.Py", value=f"[{str(discord.__version__)}](https://https://discordpy.readthedocs"
                                                 f".io)")
        embed.add_field(name="Bot Version", value=f"[1.0.0](https://www.coventry.ac.uk)")
        embed.add_field(name="About Terabyte", value="Terabyte was made by 5 University Students who are "
                                                       "studying Computer Science at Coventry University.\n\nIt was "
                                                       "made for a University Project and since than has been "
                                                       "improved and made into a new bot.", inline=False)
        embed.set_footer(text="Created by Adil, Joao, Nick, Ibra & Leo")
        await ctx.send(embed=embed)

    # Help command
    # Used for displaying help about the bot
    @commands.command(name="help", pass_context=True)
    async def help_command(self, ctx):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefix = prefixes[(str(ctx.guild.id))]
        embed = discord.Embed(title="Game Stats Help")
        embed.color = random.randint(0, 0xffffff)
        embed.add_field(name=f"{prefix}help", value="Displays this command")
        embed.add_field(name=f"{prefix}info", value='Displays info about the bot')
        embed.add_field(name=f"{prefix}ping", value="Pings the bot")
        embed.add_field(name=f"{prefix}cog load <cog>", value="Load a cog into the bot")
        embed.add_field(name=f"{prefix}cog unload <cog>", value="Unload a cog from the bot")
        embed.add_field(name=f"{prefix}cog reload <cog>", value="Reload a cog from the bot")
        embed.add_field(name=f"{prefix}gamelobby create <maxPlayers> <game>", value="Create a game lobby")
        embed.add_field(name=f"{prefix}gamelobby delete <lobbyName>", value="Delete a game lobby (Requires Admin Perms)")
        embed.add_field(name=f"{prefix}gamelobby setcategory <categoryID>", value="Set game lobby category (Requires "
                                                                                  "Admin Perms)")
        embed.add_field(name=f"{prefix}ytt", value="Checks currently trending games on YouTube")
        embed.set_footer(text="Created by Adil, Joao, Nick, Ibra & Leo")

        await ctx.send(embed=embed)


# Setup function required by discord.py
def setup(bot):
    bot.add_cog(Core(bot))
