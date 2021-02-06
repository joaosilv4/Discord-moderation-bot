# GameLobbyTickets.py
# Used to create tickets for people looking for game lobbies
# (C) João Silva

# Import required libraries
import asyncio
import discord
from discord.ext import commands
import os
import json


#
# Class: gametickets
# This class handles the ticket system
# that allows people that are looking for game lobbies
# to simple create them and join them
#
def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = discord.ext.commands.Bot(command_prefix = get_prefix, help_command=None)

class gametickets(commands.Cog):
    # Initialize the Class and bot variable
    def __init__(self, bot):
        self.bot = bot
        # self.client.loop.create_task(self.check_if_game_lobbies_are_empty())

    # Once cog is ready run this
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog "gametickets" is ready')

    @commands.group(name='gamelobby', pass_context=True)
    async def gamelobby(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Error: Invalid subcommand used. Type "' + self.bot.command_prefix + 'help" for more info')

    @gamelobby.command(name="create")
    async def create_game_lobby(self, ctx, maxPlayers, *, gamename):
        if maxPlayers.isnumeric():
            maxPlayers = int(maxPlayers)
            if 2 < maxPlayers <= 10:
                guildDataFile = checkGuildLobbyDataFileExists(str(ctx.guild.id))
                if guildDataFile != 'Null':
                    if not gamename:
                        await ctx.send('Error: Please specify a valid game name')
                        return
                    if not ctx.author.voice or not ctx.author.voice.channel:
                        await ctx.send('Error: Please join a voice channel before creating a game lobby')
                        return
                    with open(guildDataFile, 'r') as guildFile:
                        data = json.load(guildFile)
                    if not data['gameCategory']:
                        await ctx.send(f'Error: Please set a game lobby category using "{self.bot.command_prefix}'
                                       f'gamelobby setcategory <categoryID>"')
                        return
                    categoryID = str(data['gameCategory'])
                    category = getCategoryByID(ctx.message.author, categoryID)
                    if not category:
                        await ctx.send(f'Error: Please set a game lobby category using "{self.bot.command_prefix}'
                                       f'gamelobby setcategory <categoryID>"')
                        return

                    lobbyName = str(f"{ctx.message.author.name}'s {gamename} Lobby")
                    # Code is broken here
                    channel = discord.utils.get(ctx.guild.voice_channels, name=lobbyName)
                    if channel is None:
                        channel = await ctx.guild.create_voice_channel(name=lobbyName,
                                                                       category=category,
                                                                       user_limit=maxPlayers)
                        if channel is not None:
                            await ctx.message.author.move_to(channel)
                        with open(guildDataFile, 'r') as guildFile:
                            data = json.load(guildFile)

                        data['gameLobbies'].append({'channelID': channel.id})
                        with open(guildDataFile, 'w') as guildFile:
                            json.dump(data, guildFile)
                        await ctx.send(f"Successfully created game lobby: {lobbyName}")
                    else:
                        await ctx.send(f'Error: A game lobby with the name: "{lobbyName}" already exists')
                else:
                    await ctx.send('Error: An error occurred while trying to access the guild game lobby data file. '
                                   'Please try again later or contact the developers.')
            else:
                await ctx.send('Error: Please specify an amount between 2 - 10 players')
        else:
            await ctx.send('Error: Please specify a number between 2 - 10 players')

    @gamelobby.command(name="setcategory")
    @commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
    async def setcategory_game_lobby(self, ctx, *, categoryID):
        category = getCategoryByID(ctx.message.author, categoryID)
        if not category:
            await ctx.send('Error: Please enter a valid category ID and try again')
            return

        guildDataFile = checkGuildLobbyDataFileExists(str(ctx.guild.id))
        if guildDataFile != 'Null':
            with open(guildDataFile, 'r') as guildFile:
                data = json.load(guildFile)
            data['gameCategory'] = str(category.id)
            with open(guildDataFile, 'w') as guildFile:
                json.dump(data, guildFile)
            await ctx.send(
                'Successfully updated the game lobby category to "' + category.name + '" with ID: "' + str(category.id)
                + '"')
        else:
            await ctx.send('Error: An error occurred while trying to access the guild game lobby data file. '
                           'Please try again later or contact the developers.')

    @gamelobby.command(name="delete")
    @commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
    async def delete_game_lobby(self, ctx, *, lobbyName):
        lobbyChannel = discord.utils.get(ctx.guild.voice_channels, name=lobbyName)
        if lobbyChannel is None:
            await ctx.send(f'Error: The game lobby with the Name: "{str(lobbyName)}" does not exist')
            return
        if checkIfVoiceChannelIsEmpty(ctx.message.author, lobbyChannel):
            await deleteVoiceChannel(ctx.message.author, lobbyChannel, empty='NotEmpty')
            await ctx.send(f'Successfully deleted the channel with the name: "{str(lobbyName)}"')

    # @delete_game_lobby.error
    # @setcategory_game_lobby.error
    # async def game_lobby_error(self, ctx, error):
    #    if isinstance(error, commands.CheckFailure):
    #        await ctx.send("Error: You do not have the required permissions to run this command")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async def run_voice_channel_check(member, channel):
            if checkIfVoiceChannelIsEmpty(member, channel):
                await deleteVoiceChannel(member, channel)

        # User is bot
        if member.bot:
            return
        # User joined channel
        if not before.channel:
            print(f'{member.name} joined {after.channel.name}')
        # User left channel
        if before.channel and not after.channel:
            print('User left channel')
            await run_voice_channel_check(member, before.channel)
        # User switched channel
        if before.channel and after.channel:
            if before.channel.id != after.channel.id:
                print(f'{member.name} switched channels from {before.channel.name} to {after.channel.name}')
                await run_voice_channel_check(member, before.channel)
            else:
                print('An error occurred during a voice state update')

    async def check_if_game_lobbies_are_empty(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            await asyncio.sleep(300)


def checkGuildFolderExists(serverID):
    dataPath = os.path.join(os.sep, os.getcwd(), 'data')
    serverFolder = os.path.join(os.sep, dataPath, serverID)
    if os.path.exists(serverFolder):
        return True
    else:
        os.mkdir(serverFolder)
        if checkGuildFolderExists(serverID):
            return True
    return False


def checkGuildLobbyDataFileExists(serverID):
    dataPath = os.path.join(os.sep, os.getcwd(), 'data', str(serverID), 'gameLobbies.json')
    if checkGuildFolderExists(serverID):
        if os.path.exists(dataPath):
            return str(dataPath)
        else:
            with open(dataPath, "w+") as guildFile:
                guildData = guildFile.write('{'
                                            '"gameCategory": "",'
                                            '"gameLobbies": ['
                                            ']}')
                return str(dataPath)
    return 'Null'


def getCategoryByID(member, categoryID):
    category = None
    for cat in member.guild.categories:
        if str(cat.id) in str(categoryID):
            category = cat
    return category


def checkIfVoiceChannelExists(member, channel):
    guildDataFile = checkGuildLobbyDataFileExists(str(member.guild.id))
    if guildDataFile == 'Null':
        return False
    with open(guildDataFile, 'r') as guildFile:
        data = json.load(guildFile)
    if not data['gameCategory']:
        return False
    gameCategory = str(data['gameCategory'])
    category = getCategoryByID(member, gameCategory)
    if not category:
        return False
    for vc in member.guild.voice_channels:
        if str(vc.category_id) in str(category.id):
            if vc.id == channel.id:
                return True
    return False


def checkIfVoiceChannelIsEmpty(member, channel):
    if checkIfVoiceChannelExists(member, channel):
        if len(channel.members) <= 0:
            return True
    return False


async def deleteVoiceChannel(member, channel, empty=None):
    if checkIfVoiceChannelIsEmpty(member, channel) or empty == 'NoEmpty':
        try:
            guildDataFile = checkGuildLobbyDataFileExists(str(member.guild.id))
            if guildDataFile == 'Null':
                await member.send('Error: The guild data file does not exist')
                return False
            with open(guildDataFile, 'r') as guildFile:
                data = json.load(guildFile)
            for voiceChannel in data['gameLobbies']:
                channelID = voiceChannel['channelID']
                if channel.id == channelID:
                    del voiceChannel['channelID']
                    with open(guildDataFile, 'w') as guildFile:
                        json.dump(remove_empty_elements_from_array(data), guildFile)
                    channelToDelete = discord.utils.get(member.guild.voice_channels, id=channel.id)
                    await channelToDelete.delete()
            return True
        except discord.Forbidden:
            await member.send('Error: Bot is missing permissions')
            return False
        except discord.NotFound:
            await member.send('Error: Channel has already been deleted')
            return False
        except discord.HTTPException:
            await member.send('Error: A HTTPException has occurred')
            return False


def remove_empty_elements_from_array(data):
    def isEmpty(ele):
        return ele == {}

    # Is data not a list
    if not isinstance(data, (dict, list)):
        return data
    # Is data a list, if so remove empty elements
    elif isinstance(data, list):
        return [newData for newData in (remove_empty_elements_from_array(newData) for newData in data)
                if not isEmpty(newData)]
    # Data is something else
    else:
        return {newerData: newData for newerData, newData in ((newerData, remove_empty_elements_from_array(newData))
                                                              for newerData, newData in data.items())
                if not isEmpty(newData)}


# Setup function required by discord.py
def setup(bot):
    bot.add_cog(gametickets(bot))
