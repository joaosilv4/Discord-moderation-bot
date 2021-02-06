import os
import discord
import json
from discord import user
from discord.ext import commands, tasks
from itertools import cycle
import random
from googleapiclient.discovery import build


#To change prefix we need to store the prefix in a json file
def get_prefix(bot, message):  #
    with open('prefixes.json', 'r') as f: #prefixes.json is the name of the file, when u run the command it has to open the file and change the prefix to the one you have introduced and than store it
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]

bot = discord.ext.commands.Bot(command_prefix=get_prefix, help_command=None)  # help_command=None => Removes the default 'help' command / The bot has already a costum 'help' command

status = cycle(['Type $!help', 'Moderation Bot'])


###########################    Administrators / Moderators Commands    ###########################


# 'server' command build
@bot.command()
async def server(ctx):
    name = str(ctx.guild.name)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    region = str(ctx.guild.region)
    memberCount = str(ctx.guild.member_count)
    rulesChannel = str(ctx.guild.rules_channel)

    icon = str(ctx.guild.icon_url)

    embed = discord.Embed(
        author_icon=icon,
        title=name + ' - Server Information:',
        color=discord.Color.dark_red()
    )
    embed.set_author(name=str(bot.user.name), icon_url=str(bot.user.avatar_url))
    embed.set_thumbnail(url=str(ctx.guild.icon_url))
    embed.add_field(name='Owner', value=owner, inline=True)
    embed.add_field(name='Server ID', value=id, inline=True)
    embed.add_field(name='Region', value=region, inline=True)
    embed.add_field(name='Member Count', value=memberCount, inline=True)
    embed.add_field(name='Rules Channel', value=rulesChannel, inline=True)

    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def credits(ctx):

    embed = discord.Embed(
        color=discord.Color.dark_red()
    )
    embed.set_author(name=str(bot.user.name), icon_url=str(bot.user.avatar_url))
    embed.add_field(name='**Created by :**', value='`João Silva`', inline=False)
    embed.add_field(name='**Made for :**', value= '**Coventry University - Computer Science Activity Led Learning Project 1**', inline=False)

    await (ctx.channel.purge(limit=1))
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

# Start the bot if everything on the code is right
@bot.event  # client because we used client on line 5
async def on_ready():  # when the bot is ready, when he gots all the information from Discord and everything is working properly
    change_status.start()  # This command loops the bot status (line 9)
    # await client.change_presence(status=discord.Status.idle, activity=discord.Game('$!help')) 'This command set status to Playing '$!help' under the name'
    print('Bot is ready.')

#--------------------------------------------------------------------------------

# 'changeprefix' command events
@bot.event
async def on_guild_join(guild):
    with open('prefixes.json', 'r') as oppo_guild_prefix:
        prefixes = json.load(oppo_guild_prefix)
    prefixes[str(guild.id)] = '$!'  # Default value, until it gets changed
    with open('prefixes.json', 'w') as oppo_guild_prefix:
        json.dump(prefixes, oppo_guild_prefix, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as oppo_guild_prefix:
        prefixes = json.load(oppo_guild_prefix)
    prefixes.pop(str(guild.id))
    with open('prefixes.json', 'w') as oppo_guild_prefix:
        json.dump(prefixes, oppo_guild_prefix, indent=4)

#--------------------------------------------------------------------------------

# 'changeprefix' command build
@bot.command()
@commands.has_permissions(administrator=True) # Only administrators can run this command
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as oppo_guild_prefix:
        prefixes = json.load(oppo_guild_prefix)
    prefixes[str(ctx.guild.id)] = prefix
    with open('prefixes.json', 'w') as oppo_guild_prefix:
        json.dump(prefixes, oppo_guild_prefix, indent=4)
    await ctx.send(f'**Prefix changed to: {prefix} **')

# 'changeprefix' error message
@changeprefix.error
async def changeprefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        with open('prefixes.json', 'r') as oppo_guild_prefix:
            prefixes = json.load(oppo_guild_prefix)
        prefix = prefixes[(str(ctx.guild.id))]
        changeprefix = str('Please, type the command again and than type the prefix you want to use. After the change, '
                           'the command prefixes are all changed to the new prefix until another change is made with this command.')
        changeprefixt = str('**changeprefix**   `' + prefix + 'changeprefix (new prefix)`')
        embed = discord.Embed(
            title='**Command Error :**',
            color=discord.Color.dark_red()
        )
        embed.add_field(name=changeprefixt, value=changeprefix, inline=False)
        await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

# Bot activity loop
@tasks.loop(seconds=10)  # Set Loop time
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

#--------------------------------------------------------------------------------

# Bot detects when someone enters the server and prints a message
@bot.event
async def on_member_join(member):  # the bot detect a member has joined the server
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome to the server {member.mention}!') ## The bot prints in the server
    print(f'{member} has joined the server.')  ## The bot prints ths in the terminal only


# Bot detects when someone left the server
@bot.event
async def on_member_remove(member):  # detect that a member in the server as left or has been kicked
    print(f'{member} has left the server. ')

#--------------------------------------------------------------------------------

@bot.command()
@commands.has_permissions(
    administrator=True)
async def administratorHelp(ctx):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefix = prefixes[(str(ctx.guild.id))]
    description = str('*Here are the commands you can use for me.*')

    cogs = str('I will show you all the configurations I have for you to load/unload cogs and customize the bot to your server.')
    kick = str('Makes me kick a user from the server.')
    changeprefix = str('Makes me change my prefix in the server. Until another change is made with this command, all commands will have this new prefix.')
    clear = str('Makes me delete the amount of messages you want. After deleting messages, it is impossible to retrieve them again.')
    ping = str('Makes me return my latency.')
    server = str('Makes me return information about the server.')
    ban = str('Makes me ban a user from the server. The ban will prevent that person from being invited again until they are unbanned.')
    unban = str('Makes me unban a user who has been banned from the server.')
    load = str('Makes me load Cogs from the Cog file to the server.')
    unload = str('Makes me unload the Cogs from the server.')

    cogst = str('**cogs**   `' + prefix + 'cogs`')
    changeprefixt = str('**changeprefix**   `' + prefix + 'changeprefix (new prefix)`')
    cleart = str('**clear**   `' + prefix + 'clear (amount)`')
    kickt = str('**kick**   `' + prefix + 'kick [user]`')
    pingt = str('**ping**   `' + prefix + 'ping`')
    servert = str('**server**   `' + prefix + 'server`')
    bant = str('**ban**   `' + prefix + 'ban [user]`')
    unbant = str('**unban**   `' + prefix + 'unban [user]`')
    loadt = str('**load**   `' + prefix + 'load (Cog)`')
    unloadt = str('**unload**   `' + prefix + 'unload (Cog)`')

    embed = discord.Embed(
        title='__ADMINISTRATOR COMMANDS LIST : __',
        description=description,
        color=discord.Color.dark_red()
    )
    embed.set_author(name=str(bot.user.name), icon_url=str(bot.user.avatar_url))
    embed.set_thumbnail(url=str(ctx.guild.icon_url))
    embed.add_field(name=changeprefixt, value=changeprefix, inline=False)
    embed.add_field(name=cogst, value=cogs, inline=False)
    embed.add_field(name=loadt, value=load, inline=False)
    embed.add_field(name=unloadt, value=unload, inline=False)
    embed.add_field(name=kickt, value=kick, inline=False)
    embed.add_field(name=bant, value=ban, inline=False)
    embed.add_field(name=unbant, value=unban, inline=False)
    embed.add_field(name=cleart, value=clear, inline=False)
    embed.add_field(name=servert, value=server, inline=False)
    embed.add_field(name=pingt, value=ping, inline=False)


    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def createrole(ctx, arg): #create role
    guild = ctx.guild
    await guild.create_role(name=arg)
    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 40, 0)
    )
    embed.add_field(name='Role Adicionada:', value=f'Role **{arg}** has been successfully created.', inline=False)
    await (ctx.channel.purge(limit=1))
    await ctx.send(embed=embed)


@bot.command(name='addrole', aliases=['AddRole'])

async def addrole(ctx, role: discord.Role, user: discord.Member):
    await user.add_roles(role)
    await (ctx.channel.purge(limit=1))
    await ctx.send(f'**Successfully given {role.mention} to {user.mention} .**')

@bot.command(name='removerole', aliases=['RemoveRole'])
@commands.has_permissions(
    administrator=True)
async def removerole(ctx, role: discord.Role, user: discord.Member):
    if ctx.author.guild_permissions.administrator:
        await user.remove_roles(role)
        await (ctx.channel.purge(limit=1))
        await ctx.send(f'**Successfully removed {role.mention} to {user.mention}.**')

#--------------------------------------------------------------------------------

# Error message when you type a command that does not exist
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
        ### await ctx.send('**Invalid command used. Type $!help to see all the available commands.**')

#--------------------------------------------------------------------------------

# 'clear' command build / Set the bot to read some type of commands to Users that have the permission to manage messages
@bot.command()
@commands.has_permissions(manage_messages=True) # Only people who can 'manage messages'(like Administrators) can use the command
async def clear(ctx, amount: int):  # If the user does not input the amount of messages to delete, the bot automatically detects the 'error' and runs 'on_command_error' (line 51); We can set 'amount=int' if we want the bot to not detect errors
    await ctx.channel.purge(limit=amount + 1)


# 'clear' error message
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefix = prefixes[(str(ctx.guild.id))]

        clear = str('Please, type again and specify an amount of messages to delete. After deleting messages, it is impossible to retrieve them again.')
        cleart = str('**clear**   `' + prefix + 'clear (amount)`')

        embed = discord.Embed(
            title='**Command Error :**',
            color=discord.Color.dark_red()
        )
        embed.add_field(name=cleart, value=clear, inline=False)

        await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

# 'kick' command build / Set the bot to read some type of commands to Users that have the permission to manage messages
@bot.command()
@commands.has_permissions(
    administrator=True)  # Only people who can 'manage messages'(like Administrators) can use the command
async def kick(ctx, member: discord.Member, *, reason=None):  # discord.Member calls discord member to be kicked
    await member.kick(reason=reason)  # If reason is needed, we set automatically to None to kick him immediately
    await ctx.send(f'Kicked {user.mention}')  # Return 'Kicked {user}'


# 'kick' error message
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefix = prefixes[(str(ctx.guild.id))]

        kick = str('Please, type again and specify the user you want to kick. ')
        kickt = str('**kick**   `' + prefix + 'kick [user]`')

        embed = discord.Embed(
            title='**Command Error :**',
            color=discord.Color.dark_red()
        )
        embed.add_field(name=kickt, value=kick, inline=False)
        await ctx.send(embed=embed)

#--------------------------------------------------------------------------------      

# 'ban' command build / Set the bot to read some type of commands to Users that have the permission to manage messages
@bot.command()
@commands.has_permissions(
    administrator=True)  # Only people who can 'manage messages'(like Administrators) can use the command
async def ban(ctx, member: discord.Member, *, reason=None):  # discord.Member calls discord member to be kicked
    await member.ban(reason=reason)  # If reason is needed, we set automatically to None to kick him immediately
    await ctx.send(f'**Banned** {user.mention}')


# 'ban' error message
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefix = prefixes[(str(ctx.guild.id))]

        ban = str('Please, type again and specify the user you want to ban. Banning someone from the server will prevent that person from being invited again until they are unbanned.')
        bant = str('**ban**   `' + prefix + 'ban [user]`')

        embed = discord.Embed(
            title='**Command Error :**',
            color=discord.Color.dark_red()
        )
        embed.add_field(name=bant, value=ban, inline=False)

        await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

# 'unban' command build / Set the bot to read some type of commands to Users that have the permission to manage roles
@bot.command()
@commands.has_permissions(
    manage_roles=True)  # Only people who can 'manage messages'(like Administrators) can use the command
async def unban(ctx, member):  # We can only put member because we are unbanning, so he is not in the server
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):  # To see if they match
            await ctx.guild.unban(user)
            await ctx.send(f'**Unbanned** {user.name}#{user.discriminator}')  # We could use 'user.mention'
            return


# 'unban' message error
@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefix = prefixes[(str(ctx.guild.id))]

        unban = str('Please, type again and specify the user you want to unban. ')
        unbant = str('**unban**   `' + prefix + 'unban [user]`')

        embed = discord.Embed(
            title='**Command Error :**',
            color=discord.Color.dark_red()
        )
        embed.add_field(name=unbant, value=unban, inline=False)

        await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def type(ctx, arg):
    await (ctx.channel.purge(limit=1))
    await ctx.send(arg)


@bot.command()
async def embedtype(ctx, arg):
    embed = discord.Embed(
        color=discord.Color.from_rgb(255, 40, 0)
    )
    embed.add_field(name='Frase:', value=arg, inline=False)
    await (ctx.channel.purge(limit=1))
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def suggest(ctx, message):
    embed = discord.Embed(
        title='Suggestions:',
        color=discord.Color.from_rgb(255, 40, 0)
    )
    embed.set_author(name=str(bot.user.name), icon_url=str(bot.user.avatar_url))
    embed.add_field(name="Sugest:", value=message, inline=False)
    await (ctx.channel.purge(limit=1))
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------
    
@bot.command()
async def serverMembers(ctx):
    await ctx.send(ctx.guild.member_count)

#--------------------------------------------------------------------------------


@bot.command()
async def weather(ctx):
    weatherList = [
        "The weather is terrible here :/",
        "ITS SO HOT I NEED HELP",
        "The weather is cloudy over here in robot heaven",
        "It's snowing!!"
    ]
    botweather=random.choice(weatherList)
    embed=discord.Embed(title="Terabyte Bot", description = botweather)
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def game(ctx):
    gameList = [
        "I enjoy playing games such as Detroit: Become Human. I believe there will be a time where bots like us will overthrow humans. No offense of course :)",
        "I don't play games. Sorry!",
        "GTAV is a brilliant game that I play.",
        "Not playing any games right now. Currently waiting for the Cyberpunk 2077 which is getting released in a few years."
        ]
    botgame=random.choice(gameList)
    embed=discord.Embed(title="Terabyte Bot", description = botgame)
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def pickup(ctx):
    pickupLines = [
        "Allow me to ambulate by your location again if you don’t believe in love at first optical recognition.",
        "Could you grab Java with me",
        "I going to rock your world. The least you need to have is an accelerometer.",
        "Did I feel a spark between us or my CPU just malfunctioned?",
        "Since I can see myself in your service pot, there must be a mirror in your adonized Titanium exterior plating.",
        "Your father must have been a thief. See, he stole some titanium bolts and fixed them in your eyes.",
        "Did my internal fan system crash or is it just hot in here?",
        "Having run your code through my CPU all night, you must be very tired.",
        "Are you happy to see me or is that a joystick in your hand?",
        "Your chassis is out of this world; it must have been designed to function in Mars.",
        "I can see myself in your pants; are they reflective aluminum alloy?",
        "I seem to have lost my IP number. Can I have yours?",
        "Hello. I am calling to ask if I can crash at your place tonight. My name is Vista.",
        "Hey darling, I’d like to know your OS.",
        "Make a choice; my docking station orxzurs?",
        "Since you are the bomb, I’m going to commence explosive containment procedures.",
        "Want to know what I support? Portrait and landscapes mode, of course.",
        "I’m willing to convert to metric because of you."
        ]
    pickup=random.choice(pickupLines)
    embed=discord.Embed(title="Terabyte Bot", description = pickup)
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------       

@bot.command()
async def joke(ctx,):
    jokeList = [
        "What did the droid do at lunch time? ||Had a byte!:joy:||",
        "What did the man say to his dead robot? ||Rust in peace <:sadge:724682295130456115>||",
        "What do robots eat as snacks? ||Micro-chips! :joy:||",
        "Why was the robot angry? ||Because someone kept pushing its buttons :rolf:||"
    ]
    botjoke=random.choice(jokeList)
    embed=discord.Embed(title="Terabyte Bot", description = botjoke)
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------

@bot.command()
async def youtube(ctx, userinput):
    valid=0
    count=0
    api_key = 'AIzaSyA15zQB8MfRa73e--t27P04Vkyv7oDuV_A'

    # got the function from https://www.youtube.com/watch?v=th5_9woFJmk
    youtube = build('youtube', 'v3',
                    developerKey=api_key)  # from https://github.com/googleapis/google-api-python-client/blob/master/docs/start.md
    userinput = userinput.split()
    while valid==0 and count <= len(userinput):
        youtuber=userinput[count]
        request = youtube.channels().list(
            part='contentDetails,statistics',
            forUsername=youtuber  # need channel username
        )
        response = request.execute()   # Returns information on youtube channel
        info=response['pageInfo']
        if info["totalResults"] >=1:
            for item in response['items']:
                sub_count = item['statistics']['subscriberCount']
                if int(sub_count)>=50000:
                    valid=1
        count =count+1

    for item in response['items']:
        sub_count = item['statistics']['subscriberCount']
        view_count = item['statistics']['viewCount']
        video_count = item['statistics']['videoCount']
        average_view_per_video = int(view_count) / int(video_count)  # finds the average views for video
        average_view_per_video_rounded = round(average_view_per_video)  # rounds the average amount of views
        await ctx.send("Sub count is: " + str(sub_count))
        await ctx.send("View count is: " + str(view_count))
        await ctx.send("Video count is: " + str(video_count))
        await ctx.send("Average view per video is: " + str(average_view_per_video_rounded))
        # this prints out the subcount view count video count and average views

#--------------------------------------------------------------------------------       

@bot.event
# Handle all command errors
async def on_command_error(ctx, error):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefix = prefixes[(str(ctx.guild.id))]
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            'The command is missing some arguments, type ' + prefix + 'help to find the correct usage')
    else:
        await ctx.send('The following error has occurred: ' + str(error))

 #--------------------------------------------------------------------------------

    # Load command
    # Used for loading cogs
@bot.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}!')
    await ctx.send(f'Loaded Cog: {extension}')

    # Unload command
    # Used for unloading cogs
@bot.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded Cog: {extension}')
    
#--------------------------------------------------------------------------------

# Set cogs (Cogs File)
for filename in os.listdir('./cogs'):  # create a loop when the bot starts it runs every file that starts with '.py' loaded like a 'Cog' // './' means current directory that I'm in
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')  # Takes out the last 3 digits('.py'), because we want to run the file as 'cogs.example' and not 'cogs.example.py'
