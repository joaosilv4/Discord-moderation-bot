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
async def highRatedGames(self, ctx):
    responses = {0: '"God of War"',
                     1: '"Call of Duty: Modern Warfare 2"',
                     2: '"Final Fantasy IX"',
                     3: '"BioShock Infinite"',
                     4: '"World of Goo"',
                     5: '"Metal Gear Solid V: The Phantom Pain"',
                     6: '"Portal 2"',
                     7: '"Madden NFL 2003"',
                     8: '"The Last of Us"',
                     9: '"The Legend of Zelda: Majoras Mask"',
                     10: '"The Legend of Zelda: A Link to the Past"',
                     11: '"Halo 2"',
                     12: '"Gran Turismo 3: A-Spec"',
                     13: '"Red Dead Redemption"',
                     14: '"Clash Royale"',
                     15: '"LittleBigPlanet"',
                     16: '"Grand Theft Auto: Vice City"',
                     17: '"Grand Theft Auto: San Andreas"',
                     18: '"Baldurs Gate II: Shadows of Amn"',
                     19: '"Metal Gear Solid 2: Sons of Liberty"',
                     20: '"Gran Turismo"',
                     21: '"The Legend of Zelda: The Wind Waker"',
                     22: '"Half-Life"',
                     23: '"The Elder Scrolls V: Skyrim"',
                     24: '"The Legend of Zelda: Twilight Princess"',
                     25: '"Mass Effect 2"',
                     26: '"Tekken 3"',
                     27: '"Batman: Arkham City"',
                     28: '"The Orange Box"',
                     29: '"Resident Evil 4"'}

    values = {
            0: 'God of War is an action-adventure game franchise created by David Jaffe at Sony Santa Monica Studio based'
               ' in ancient mythology. The story follows Kratos, a Spartan warrior who was tricked into killing his family'
               ' by his former master, the Greek God of War Ares.',
            1: 'Call of Duty: Modern Warfare 2 is a 2009 first-person shooter game developed by Infinity Ward and published'
               ' by Activision. It is the sixth installment in the Call of Duty series and the direct sequel to Call of '
               'Duty 4: Modern Warfare, continuing the storyline. It was released worldwide on November 10, 2009.',
            2: 'Every character is memorable and unique. FINAL FANTASY IX features one of the quirkiest casts in the '
               'entire FINAL FANTASY series - maybe even in all of gaming. Every character in the game is utterly '
               'distinct - both visually and in terms of their personality.',
            3: 'BioShock Infinite is a first-person shooter video game developed by Irrational Games and published by '
               '2K Games. The game is set in the year 1912 and follows its protagonist, former Pinkerton agent Booker '
               'DeWitt, who is sent to the airborne city of Columbia to find a young woman, Elizabeth, who has been held'
               ' captive there for most of her life. Though Booker rescues Elizabeth, the two become involved with the '
               'citys warring factions: the nativist and elite Founders that rule Columbia and strive to keep its '
               'privileges for White Americans, and the Vox Populi, underground rebels representing the underclass of '
               'the city. ',
            4: 'World of Goo is a puzzle video game developed and published by independent game developer 2D Boy. A '
               'physics-based puzzler, World of Goo has the player use small balls of goo to create bridges and similar'
               ' structures over chasms and obstacles to help other goo balls reach a goal point, with the challenge to'
               ' use as few goo balls as possible to build this structure.',
            5: 'Metal Gear Solid V: The Phantom Pain is an open world stealth game developed by Kojima Productions and '
               'published by Konami. The Phantom Pain received perfect review scores from several publications and was '
               'described as one of the greatest stealth games of all time. A complete edition that bundles The Phantom '
               'Pain and Ground Zeroes together, titled Metal Gear Solid V: The Definitive Experience, was released in '
               'October 2016.',
            6: 'Portal 2 is a puzzle-platform game developed by Valve. It was released in April 2011 for Windows, Mac OS'
               ' X, Linux, PlayStation 3, and Xbox 360. The digital PC version is distributed online by Valve Steam '
               'service, while all retail editions were distributed by Electronic Arts.',
            7: 'Madden NFL 2003 is an American football simulation video game based on the NFL that was developed by EA'
               ' Tiburon and Budcat Creations and published by EA Sports.',
            8: 'The Last of Us is a 2013 action-adventure game developed by Naughty Dog and published by Sony Computer '
               'Entertainment. Players control Joel, a smuggler tasked with escorting a teenage girl, Ellie, across a '
               'post-apocalyptic United States. The Last of Us is played from a third-person perspective. Players use '
               'firearms and improvised weapons, and can use stealth to defend against hostile humans and cannibalistic'
               ' creatures infected by a mutated fungus in the genus Cordyceps. In the online multiplayer mode, up to '
               'eight players engage in cooperative and competitive gameplay.',
            9: 'The Legend of Zelda: Majoras Mask is an action-adventure game developed and published by Nintendo for '
               'the Nintendo 64. It featured enhanced graphics and several gameplay changes from its predecessor, though'
               ' it reused a number of elements and character models, which the games creators called a creative decision'
               ' made necessary by time constraints.',
            10: 'The Legend of Zelda: A Link to the Past is an action-adventure game developed and published by Nintendo'
                ' for the Super Nintendo Entertainment System. It is the third game in The Legend of Zelda series and '
                'was released in 1991 in Japan and 1992 in North America and Europe.',
            11: 'Halo 2 is a 2004 first-person shooter game developed by Bungie and published by Microsoft Game Studios.'
                ' Released for the Xbox, the game is the second installment in the Halo franchise and the sequel to 2001'
                ' critically acclaimed Halo: Combat Evolved. The game features a new game engine, added weapons and '
                'vehicles, and new multiplayer maps.',
            12: 'Gran Turismo 3: A-Spec is a 2001 racing game, the first in the Gran Turismo series released for the '
                'PlayStation 2. During its demonstration at E3 2000 and E3 2001 the games working title was Gran Turismo'
                ' 2000. The game was a critical and commercial success and went on to become one of the best-selling '
                'video games of all time. Its aggregate score of 94.54% on GameRankings makes it the second-highest rated'
                ' racing video game of all time. It has been listed as one of the greatest video games of all time.',
            13: 'Red Dead Redemption is a 2010 action-adventure game developed by Rockstar San Diego and published by '
                'Rockstar Games. A spiritual successor to 2004s Red Dead Revolver, it is the second game in the Red Dead'
                ' series. Red Dead Redemption is set during the decline of the American frontier in the year 1911 and '
                'follows John Marston, a former outlaw whose wife and son are taken hostage by the government in ransom'
                ' for his services as a hired gun. Having no other choice, Marston sets out to bring three members of his'
                ' former gang to justice.',
            14: 'Clash Royale is a freemium real-time strategy video game developed and published by Supercell. The game'
                ' combines elements from collectible card games, tower defense, and multiplayer online battle arena. The'
                ' game was released globally on March 2, 2016. Clash Royale reached $1 billion in revenue in less than a'
                ' year on the market.',
            15: 'LittleBigPlanet (LBP) is a puzzle platform video game series created by British developer Media Molecule'
                ' and published by Sony Computer Entertainment on multiple PlayStation platforms. All of the games in '
                'the series put a strong emphasis on user-generated content and are based on the series tagline "Play, '
                'Create, Share". The tagline represents the three core elements of the series: playing alone or with '
                'others locally (on the same console) or online, creating new content using the in-game creation tools,'
                ' and sharing creations and discoveries online with other players.',
            16: 'Grand Theft Auto: Vice City is a 2002 action-adventure game developed by Rockstar North and published '
                'by Rockstar Games as part of the Grand Theft Auto series. Set in 1986 within the fictional Vice City, '
                'based on Miami, the game follows the exploits of mobster Tommy Vercetti after his release from prison. '
                'Upon being caught up in an ambushed drug deal, he seeks out those responsible while slowly building a '
                'criminal empire and seizing power from other criminal organisations in the city.',
            17: 'Grand Theft Auto: San Andreas is a 2004 action-adventure game developed by Rockstar North and published'
                ' by Rockstar Games. It is the seventh title in the Grand Theft Auto series, and the follow-up to the '
                '2002 game Grand Theft Auto: Vice City. It was released in October 2004 for PlayStation 2, and in June '
                '2005 for Microsoft Windows and Xbox. The game, set within an open world environment that players can '
                'explore and interact with at their leisure, focuses on the story of former gangster Carl "CJ" Johnson,'
                ' who is brought back home by the death of his mother, only to become involved in a long journey that '
                'sees him exploring the fictional U.S. state of San Andreas, which is heavily based on California and '
                'Nevada.',
            18: 'Baldurs Gate II: Shadows of Amn is a role-playing video game developed by BioWare and published by '
                'Interplay Entertainment. It is the sequel to Baldurs Gate (1998) and was released for Microsoft Windows'
                ' in September 2000. Like Baldurs Gate, the game takes place in the Forgotten Realms—a fantasy campaign'
                ' setting—and is based on the Advanced Dungeons & Dragons 2nd edition rules. Powered by BioWares Infinity'
                ' Engine, Baldurs Gate II uses an isometric perspective and pausable real-time gameplay. The player '
                'controls a party of up to six characters, one of whom is the player-created protagonist, while the others'
                ' are certain characters recruited from the game world.',
            19: 'Metal Gear Solid 2: Sons of Liberty[a] is a stealth game developed and published by Konami for the '
                'PlayStation 2 on November 13, 2001. It is the fourth Metal Gear game written and directed by Hideo '
                'Kojima, the seventh overall game in the series and is a direct sequel to the original Metal Gear Solid.'
                ' An expanded edition, titled Metal Gear Solid 2: Substance, was released the following year for Xbox '
                'and Microsoft Windows in addition to the PlayStation 2.',
            20: 'Gran Turismo[a] (GT) is a series of racing simulation video games developed by Polyphony Digital. '
                'Developed for PlayStation systems, Gran Turismo games are intended to emulate the appearance and '
                'performance of a large selection of vehicles, most of which are licensed reproductions of real-world '
                'automobiles. Since the franchises debut in 1997, over 80 million units have been sold worldwide for the'
                ' PlayStation, PlayStation 2, PlayStation 3, PlayStation 4, and PlayStation Portable, making it the '
                'highest selling video game franchise under the PlayStation brand.',
            21: 'The Legend of Zelda: The Wind Waker[b] is an action-adventure game developed and published by Nintendo '
                'for the GameCube home video game console. The tenth installment in The Legend of Zelda series, it was '
                'released in Japan in December 2002, in North America in March 2003, and in Europe in May 2003.',
            22: 'Half-Life is a first-person shooter video game developed by Valve and published by Sierra Studios for '
                'Microsoft Windows in 1998. It was Valves debut product and the first game in the Half-Life series. '
                'Players assume the role of Gordon Freeman, a scientist who must escape the Black Mesa Research Facility'
                ' after it is invaded by aliens. The core gameplay consists of fighting alien and human enemies with a '
                'variety of weapons and solving puzzles.',
            23: 'The Elder Scrolls V: Skyrim is an open world action role-playing video game developed by Bethesda Game '
                'Studios and published by Bethesda Softworks. It is the fifth main installment in The Elder Scrolls '
                'series, following The Elder Scrolls IV: Oblivion, and was released worldwide for Microsoft Windows, '
                'PlayStation 3, and Xbox 360 on November 11, 2011. The games main story revolves around the players '
                'character, the Dragonborn, on their quest to defeat Alduin the World-Eater, a dragon who is prophesied '
                'to destroy the world.',
            24: 'The Legend of Zelda: Twilight Princess is an action-adventure game developed and published by Nintendo '
                'for the GameCube and Wii home video game consoles. It is the thirteenth installment in the series The '
                'Legend of Zelda. Originally planned for release exclusively on the GameCube in November 2005, Twilight '
                'Princess was delayed by Nintendo to allow its developers to refine the game, add more content, and port'
                ' it to the Wii.[4] The Wii version was a launch game in North America in November 2006, and in Japan, '
                'Europe, and Australia the following month. The GameCube version was also released worldwide in December'
                ' 2006, and was the final first-party game released for the console.'}
    eletron = []
    proton = []
    for x in range(5):
        tita = random.randrange(24)
        while responses.get(tita) in eletron:
            tita = random.randrange(24)
        eletron.append(responses.get(tita))
        proton.append(values.get(tita))
    embed = discord.Embed(
        title='Suggestions:',
        color=discord.Color.from_rgb(255, 40, 0)
    )
    embed.add_field(name=eletron[0], value=proton[0], inline=False)
    embed.add_field(name=eletron[1], value=proton[1], inline=False)
    embed.add_field(name=eletron[2], value=proton[2], inline=False)
    embed.add_field(name=eletron[3], value=proton[3], inline=False)
    embed.add_field(name=eletron[4], value=proton[4], inline=False)
    await ctx.send("I have some suggestions:")
    await ctx.send(embed=embed)

#--------------------------------------------------------------------------------   
    
# '8ball' command build
@bot.command(aliases=['8ball'])  # abreviations and other names u can use to run this command as well as '_8ball'
async def _8ball(self, ctx, *, question):
    responses = ['It is certain.',
                 'Hmm, Yes.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes - Definitly.',
                 'You may rely on it.',
                 'As I see it, yes.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Concentrate and ask again.',
                 'My reply is no.',
                 'Hmm, No',
                 'My sources say no.',
                 'Very doubtful.']
    await ctx.send(f'**Question:** {question}\n**Answer:** {random.choice(responses)}')

    
# '8ball' error message
@_8ball.error
async def _8ball_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('**Please type the command again and make a question.**')

#--------------------------------------------------------------------------------

@bot.command()
async def youtube(ctx, userinput):
    valid=0
    count=0
    api_key = #'[api_key]'

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
