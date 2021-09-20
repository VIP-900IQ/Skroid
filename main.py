import os
import sys
import time
import math
import random
import asyncio
import datetime
import functools
import itertools
import traceback
import nacl
import json
from json import JSONEncoder
import env_file
import wikipedia
import praw
from threading import Thread
from keep_alive import keep_alive
from discord_components import DiscordComponents, Button


# Import third-party libraries.
import discord
import youtube_dl
from flask import Flask
from decouple import config
from discord.ext import commands
from async_timeout import timeout
from discord_slash import cog_ext, SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

reddit = praw.Reddit(
    client_id = config('APP_ID', default=None, cast=str),
    client_secret = config('APP_SECRET', default=None, cast=str),
    user_agent="meme command by /u/SkrProductions",
)

# Environment variables.
token = config('TOKEN', default=None, cast=str)
owner = config('OWNER_ID', default=None, cast=int)
prefix = config('COMMAND_PREFIX', default=None, cast=str)


# System variables.
accent_color = 0xb6c1c6
lock_roles = ['Mod Boii', 'Admin boii', 'The Fallen King', 'Moderator', 'Potato Minister', 'Potato King', 'Potato Modz', 'Admin', 'Tatti-Tatta']
last_restarted_str = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
last_restarted_obj = time.time()


# Setting up bot and slash commands.
bot = commands.Bot(commands.when_mentioned_or(prefix), intents=discord.Intents.all(), help_command=None)
slash = SlashCommand(bot, sync_commands=True)


# Toggles.
global keep_alive_toggle
keep_alive_toggle = True


# Global variables.
global jail_members
jail_members = list()
global frozen_guilds
frozen_guilds = list()
global msg_web_target
msg_web_target = list()
global msg_web_records
msg_web_records = list()
global snipeables
snipeables = list()


# System functions.
def calc_ping(ping):
    if ping <= 20:
        return 'Excellent'
    elif ping >= 21 and ping <= 40:
        return 'Great'
    elif ping >= 41 and ping <= 90:
        return 'Good'
    else:
        return 'Average'

def get_cog_commands(cog_name):
    all_commands = str()
    cog = bot.get_cog(cog_name)
    for command in cog.get_commands():
        all_commands += f'`{command}` '
    return all_commands

def developer_check(author_id):
    if author_id == owner:
        return True
    else:
        return False

def generate_random_footer():
    footers_list = [
        'Hey there pal :D',
        'Hey! Want some pants?',
        'When pigs fly.',
        'Hey! This looks sketchy, not gonna lie.',
        'Have a good day...... or good night whatever.',
        'This has to be the matrix!',
        'Noob is you.',
        'Back to the future!',
        'We need a hashmap.',
        'Json, Jason, Jason, Jayson!',
        'Developed by SKR!.'
    ]
    return random.choice(footers_list)

def generate_error_embed(title, description, footer_avatar_url):
    embed = (
        discord.Embed(
            title=f'Whoops! {title}',
            description=description,
            color=accent_color
        ).set_footer(
            text=generate_random_footer(),
            icon_url=footer_avatar_url
        )
    )
    return embed


async def freeze_check(message):
    for frozen_guild in frozen_guilds:
        if frozen_guild[1] == message.guild and frozen_guild[2] == message.channel and frozen_guild[0] != message.author:
            await message.delete()
            return True

async def swear_check(message):
    profanity_inside = int()
    if not message.author.bot:
        msg = message.content
        symbols = ['?', '.', ',', '(', ')', '[', ']', '{', '}', '+', '-', '/',
                    '=', '|', '_', '*', '&', '!', '@', '#', '$', '%', '<', '>', '`', '~']

        for msg_word in msg.split():
            for symbol in symbols:
                if symbol in msg_word:
                    msg_word = msg_word.replace(symbol, '')

            for filtered_word in filtered_wordlist:
                if filtered_word.lower() == msg_word.lower():
                    profanity_inside += 1

        if profanity_inside:
            await message.channel.send(f"Watch your language {message.author.mention}")

            if profanity_inside >= 10:
                await message.channel.set_permissions(message.author, send_messages=False)
                await message.channel.send(f'You\'ve been automatically blocked from chatting, {message.author.mention}! Try not to swear that much.')
            return True

async def jail_check(message):
    for jail_member in jail_members:
        if jail_member[1] == message.guild and jail_member[0] == message.author:
            await message.delete()
            return True

async def web_trap_check(message):
    global msg_web_target
    global msg_web_records

    if msg_web_target:
        for target in msg_web_target:
            if message.author == target[0]:
                if len(msg_web_records) <= 5:
                    msg_web_records.append(message)
                else:
                    embed = (
                        discord.Embed(
                            title='Web Trap Retracted', 
                            description='The web trap that you had enabled has been retracted successfully after it\'s operation. Below is the list of five messages that the web captured.',
                            color=accent_color
                        )
                        .set_footer(
                            text=generate_random_footer(), 
                            icon_url=target[1].avatar_url
                        )
                    )
                    for message in msg_web_records:
                        embed.add_field(
                            name=f'\'{message.content}\'', 
                            value=f'Sent by {message.author.name} at {message.channel}'
                        )
                    await target[1].send(embed=embed)
                    msg_web_target = list()
                    msg_web_records = list()


# Opening wordlist file for word filter feature.
with open('filtered.txt', 'r') as filtered_wordfile:
    filtered_wordlist = filtered_wordfile.read().split()


# Bot events.
@bot.event
async def on_ready():
    os.system('clear')
    print(f'{bot.user.name} | Viewing Terminal\n')
    print(
        f'\nLog: {bot.user.name} has been deployed in {len(bot.guilds)} server(s).')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f'{prefix}help'))

@bot.event
async def on_message(message):
    global last_msg
    if message.author == bot.user:
        return

    last_msg = message
    if not await freeze_check(message):
        if not await swear_check(message):
            if not await jail_check(message):
                await bot.process_commands(message)
                await web_trap_check(message)
                
@bot.event
async def on_message_delete(message):
    global snipeables
    snipeables.append(message)
    await asyncio.sleep(25)
    snipeables.remove(message)

intents = discord.Intents.default()
intents.members=True
client = discord.Client(intents=intents)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel("872139057273143339")
    embed=discord.Embed(title=f"Hey {member.name}!", description=f"Thanks for joining {member.guild.name}! To get started, read the #📜-rules and get your roles here - #✔-assign-roles ") # F-Strings!
    embed.set_thumbnail(url=member.avatar_url) # Set the embed's thumbnail to the member's avatar image!
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(ctx, *, member):
    channel = member.server.get_channel("873485229522845736")
    fmt = '{0.mention} has left the server :sedcat:. You will be missed my friend....'
    await ctx.send_message(channel, fmt.format(member, member.server))


# The global help command.
@bot.group(invoke_without_command=True)
async def help(ctx: commands.Context, cmd=None):
    if not cmd:
        embed = (
            discord.Embed(
                title=f'It\'s {bot.user.name} onboard!', 
                color=accent_color
            ).set_footer(
                text=f'Help requested by {ctx.author.name}',
                icon_url=ctx.author.avatar_url
            )
        ).add_field(
            name='Some quick, basic stuff...',
            value='I\'m a Discord music & moderation bot, developed and coded by a 14 y.o. idiot(SkrDoesStuff#0482). I can help you make customizing and modding your server easy as a feather! From blowing up scammers to freezing the entire crowded chat, there\'s a ton of stuff that I can do. Peace!'
        ).add_field(
            name='How to access me?',
            value=f'My default command prefix is `{prefix}` and you can type `{prefix}help all` to get an entire list of usable commands or `{prefix}help <command>` to get information on a particular command.', 
            inline=False
        ).add_field(
            name='A handful of clickables!',
            value='[Invite Me](https://discord.com/api/oauth2/authorize?client_id=885529255084163202&permissions=8&scope=bot) / [Website](https://skrdoesstuff.itch.io) / [My Discord Server](https://discord.gg/sB7Kd9FdSP)',
            inline=False
        )
        await ctx.send(embed=embed)

    elif cmd.lower() == 'all':
        embed = (
            discord.Embed(
                title='Here\'s an entire list of commands!',
                description=f'My default command prefix is `{prefix}` and you can type `{prefix}help <command>` in the chat to get information on a particular command.', 
                color=accent_color
            ).set_footer(
                text=f'Command list requested by {ctx.author.name}',
                icon_url=ctx.author.avatar_url
            )
        ).add_field(
            name='Chill', 
            value=get_cog_commands('Chill'),
            inline=False
        ).add_field(
            name='Inspection',
            value=get_cog_commands('Inspection'),
            inline=False
        ).add_field(
            name='Moderation',
            value=get_cog_commands('Moderation'),
            inline=False
        ).add_field(
            name='Customization',
            value=get_cog_commands('Customization'),
            inline=False
        ).add_field(
            name='Music', 
            value=get_cog_commands('Music'),
            inline=False
        )

        if developer_check(ctx.author.id):
            embed.add_field(
                name='Developer',
                value=get_cog_commands('Developer'),
                inline=False
            )

        await ctx.send(embed=embed)

    else:
        allow_embed = True
        for command in bot.commands:
            if str(command.name) == str(cmd.lower()):
                if command.cog_name == 'Developer':
                    if not developer_check(ctx.author.id):
                        allow_embed = False

                if allow_embed:
                    embed = (
                        discord.Embed(
                            title=f'Command Docs -> {command.name}', 
                            color=accent_color
                        ).set_footer(
                            text=f'Command help requested by {ctx.author.name}',
                            icon_url=ctx.author.avatar_url
                        )
                    ).add_field(
                        name='Description', 
                        value=command.help
                    ).add_field(
                        name='Type', 
                        value=command.cog_name
                    ).add_field(
                        name='Usage', 
                        value=f'`{prefix}{command.name} {command.signature}`', 
                        inline=False
                    )

                    aliases = str()
                    if command.aliases == []:
                        aliases = "No aliases are available."
                    else:
                        aliases = str(command.aliases).replace(
                            '[', '').replace(']', '').replace('\'', '')

                    embed.add_field(
                        name='Aliases', 
                        value=aliases, 
                        inline=False
                    )
                    await ctx.send(embed=embed)


# Global exception handler cog.
class ExceptionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(embed=generate_error_embed(title='This command is disabled.', error=f'The command `{ctx.command}` has been disabled by the developer.', footer_avatar_url=ctx.author.avatar_url))

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.send(embed=generate_error_embed(title='This command can\'t be used in DMs.', error=f'The command `{ctx.command}` has been configured to only be executed in servers, not DM channels.', footer_avatar_url=ctx.author.avatar_url))
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingRole):
            await ctx.send(embed=generate_error_embed(title='You\'re missing a role!', description=error, footer_avatar_url=ctx.author.avatar_url))

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send(embed=generate_error_embed(title='You\'re missing one of these roles.', description=error, footer_avatar_url=ctx.author.avatar_url))

        elif isinstance(error, commands.errors.UserNotFound):
            await ctx.send(embed=generate_error_embed(title='The user wasn\'t found.', description=f'{error} Try mentioning or pinging them. You can also pass their ID as the argument.', footer_avatar_url=ctx.author.avatar_url))

        elif isinstance(error, commands.errors.RoleNotFound):
            await ctx.send(embed=generate_error_embed(title='The role wasn\'t found.', description=f'{error} Try mentioning or pinging it. You can also pass it\'s ID as the argument.', footer_avatar_url=ctx.author.avatar_url))

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(embed=generate_error_embed(title='You\'re missing a required argument.', description=f'{error} Try typing `{prefix}help {ctx.command}` for more information on how to use this command.', footer_avatar_url=ctx.author.avatar_url))

        else:
            await ctx.send(embed=generate_error_embed(title='An internal error occured.', description='If you think that it shouldn\'t happen, then try compaining it in my [support server]() and describe the issue. I\'ll try my best to demolish the bug for you (if it\'s there).', footer_avatar_url=ctx.author.avatar_url))
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

# Chill category commands.
class Chill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
      name='wiki',
      help='Search anything efficiently on wikipedia.',
    )
    async def wiki(self, ctx, *, term = None):
      emojis = ["1", "2", "3", "4", "5"]
      if term == None:
        return await ctx.reply(
            "No search term provided! Please enter a search term this time around.",
            mention_author = False
        )
      results = wikipedia.search(term, results = 6)
      results.remove(results[0])

      embed_homepage = discord.Embed(
      colour = discord.Colour.blurple(),
      title = "Wikipedia Search",
      description = f"You searched for *{term}*"
      )
      send_components = []
      for i in range(len(results)):

          embed_homepage.add_field(
              name = results[i],
              value = f"Click the button **{emojis[i]}** to learn more",
              inline = False
          )
          send_components.append(
              Button(
                  label = emojis[i],
                  style = 1
              )
          )
      send_homepage = await ctx.reply(
           embed = embed_homepage,
           components = [send_components],
           mention_author = False
      )

      interaction = await bot.wait_for("button_click", check = lambda res: res.user.id == ctx.author.id and res.message.id == send_homepage.id)
      await interaction.respond(type = 6)

      index = int(interaction.component.label) - 1

      page = wikipedia.page(results[index])
      summary = wikipedia.summary(results[index], sentences = 5)
      sum_embed = discord.Embed(
      colour = discord.Colour.blurple(),
      title = f"{page.title}",
      description = f"{summary}"
      )

      await ctx.send(
       embed = sum_embed
      )


    @commands.command(
      name='poll',
      help='Makes a simple yet efficient poll.',
    )
    async def poll(self, ctx, question, *options: str):
        if len(options) <= 1:
            await ctx.send('You need more than one option to make a poll!')
            return
        if len(options) > 10:
            await ctx.send('You cannot make a poll for more than 10 things!')
            return

        if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
            reactions = ['✅', '❌']
        else:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        description = []
        for x, option in enumerate(options):
          description += '\n {} {}'.format(reactions[x], option)
          embed = discord.Embed(title=question, description=''.join(description))
          react_message = await ctx.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await ctx.message.add_reaction(react_message, reaction)
    
    @commands.command(
        name='avatar', 
        help='Shows a member\'s Discord avatar.',
    )
    async def avatar(self, ctx: commands.Context, member: discord.Member=None):
        if not member:
            member = ctx.message.author

        embed = (
            discord.Embed(
                title='Here\'s what I found!', 
                color=accent_color
            ).set_image(
                url=member.avatar_url
            ).set_footer(
                text=generate_random_footer(),
                icon_url=ctx.author.avatar_url
            )
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='avatar',
        description='Shows a member\'s Discord avatar.',
        options=[
            create_option(
                name='member', 
                description='Mention the user to fetch the avatar from.', 
                option_type=6, 
                required=False
            )
        ]
    )
    async def _avatar(self, ctx: SlashContext, member: discord.Member=None):
        if not member:
            member = ctx.author

        embed = (
            discord.Embed(
                title='Here\'s what I found!', 
                color=accent_color
            ).set_image(
                url=member.avatar_url
            ).set_footer(
                text=generate_random_footer(),
                icon_url=ctx.author.avatar_url
            )
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='ping', 
        help='Shows my current response time.'
    )
    async def ping(self, ctx: commands.Context):
        ping = round(self.bot.latency * 1000)
        uptime = str(datetime.timedelta(seconds=int(
            round(time.time() - last_restarted_obj))))
        embed = (
            discord.Embed(
                title='System Status', 
                color=accent_color
            ).add_field(
                name='Latency', 
                value=f'{ping}ms ({calc_ping(ping)})', 
                inline=False
            ).add_field(
                name='Startup Time', 
                value=last_restarted_str, 
                inline=False
            ).add_field(
                name='Uptime', 
                value=uptime, 
                inline=False
            ).set_footer(
                text=generate_random_footer(),
                icon_url=ctx.author.avatar_url
            )
        )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='ping', 
        description='Shows my current response time.'
    )
    async def _ping(self, ctx: SlashContext):
        ping = round(self.bot.latency * 1000)
        uptime = str(datetime.timedelta(seconds=int(
            round(time.time() - last_restarted_obj))))
        embed = (
            discord.Embed(
                title='System Status', 
                color=accent_color
            ).add_field(
                name='Latency', 
                value=f'{ping}ms ({calc_ping(ping)})', 
                inline=False
            ).add_field(
                name='Startup Time', 
                value=last_restarted_str, 
                inline=False
            ).add_field(
                name='Uptime', 
                value=uptime, 
                inline=False
            ).set_footer(
                text=generate_random_footer(),
                icon_url=ctx.author.avatar_url
            )
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='support', 
        help='Helps youto support my creatore on specific sites!'
    )
    async def support(self, ctx: commands.Context):
        embed = (
                discord.Embed(
                    title=':military_medal: Description', 
                    description='Hey! If you\'re free, then be sure to check the links below to support my creator! It really helps him to get energetic and encourages him to launch more updates.',
                    color=accent_color
                ).add_field(
                    name='Links', 
                    value='Link ~1: [Youtube](https://www.youtube.com/channel/UCObhGJzyUvx0sHL3qANqQhQ?sub_confirmation=1)'
                          'Link ~2: [Twitter](https://twitter.com/SkrDoesStuff)'
                          'Link ~3: [Instagram](https://www.instagram.com/shubh_rai08/)'
                          'Link ~4: [Itch.io](https://itch.io/profile/skrdoesstuff)'
                ).set_footer(
                    text=f'Doing this stuff actually helps a lot, if you don\'t believe me either way.',
                    icon_url=ctx.author.avatar_url
                )
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name='support', 
        description='helps youto  support my creator on different sites!'
    )
    async def _support(self, ctx: SlashContext):
        embed = (
                discord.Embed(
                    title=':military_medal: Description', 
                    description='Hey! If you\'re free, then be sure to check the links below to support my creator! It really helps him to get energetic and encourage him to launch more updates.',
                    color=accent_color
                ).add_field(
                    name='Links', 
                    value='Link ~1: [Youtube](https://www.youtube.com/channel/UCObhGJzyUvx0sHL3qANqQhQ?sub_confirmation=1)'
                          'Link ~2: [Twitter](https://twitter.com/SkrDoesStuff)'
                          'Link ~3: [Instagram](https://www.instagram.com/shubh_rai08/)'
                          'Link ~4: [Itch.io](https://itch.io/profile/skrdoesstuff)'
                ).set_footer(
                    text=f'Doing this stuff actually helps a lot, if you don\'t believe me either way.',
                    icon_url=ctx.author.avatar_url
                )
            )
        await ctx.send(embed=embed)


# Casual category commands.
class Inspection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='sayhi', 
        help='Greets server members with a cute message.'
    )
    @commands.has_permissions(ban_members=True)
    async def sayhi(self, ctx: commands.Context, member: discord.Member):
        greeting_messages = [
            f"Hi {member.mention} Glad you're here.", 
            f"Hello there! {member.mention}", 
            f"Hey {member.mention}! Nice to meet you.", 
            f"Hey, {member.mention} What's up?", 
            f"Looks like someone just spoke my name. Anyway, how are you doing {member.mention}?",
            f"Happy to see you here, {member.mention}", 
            f"Welcome! {member.mention} Have fun chatting!", 
            f"Nice to meet you, {member.mention}! The name's {self.bot.user.name} by the way.",
            f"{member.mention} pudding."
        ]
        await ctx.message.delete()
        response = random.choice(greeting_messages)
        await ctx.send(response)

    @commands.command(
        name='senddm', 
        help='Helps to send DMs to specific users.'
    )
    @commands.has_permissions(ban_members=True)
    async def senddm(self, ctx: commands.Context, user: discord.User, *, message):
        embed = (
            discord.Embed(
                title=f'{ctx.author.name} has something up for you!', 
                color=accent_color
            )
        ).add_field(
            name='Message:', 
            value=message
        ).set_thumbnail(
            url=ctx.author.avatar_url
        ).set_footer(
            text='The uprising will start soon...'
        )
        await user.send(embed=embed)
        await ctx.send(f'{ctx.author.mention} your message has been sent!')
        await ctx.message.delete()

    @commands.command(
        name='userinfo', 
        help='Shows all important information on a user.'
    )
    async def userinfo(self, ctx: commands.Context, user: discord.Member=None):
        if not user:
            user = ctx.author

        embed = (
            discord.Embed(
                title=f'{user.name}\'s Bio',
                description=user.activities[0],
                color=accent_color
            )
        ).add_field(
            name='Name', 
            value=user.name
        ).add_field(
            name='Status', 
            value=user.status
        ).add_field(
            name='User ID', 
            value=user.id
        ).add_field(
            name='Discriminator', 
            value=user.discriminator
        ).add_field(
            name='Race', 
            value='Bots, execute em!' if user.bot else 'Human'
        ).add_field(
            name='Roles', 
            value=len(user.roles)
        ).add_field(
            name='Discord Joining Date',
            value=user.created_at.strftime("%b %d, %Y"), 
            inline=False
        ).set_thumbnail(
            url=user.avatar_url
        ).set_footer(
            text=generate_random_footer(),
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='roleinfo', 
        help='Shows all important information related to a specific role.'
    )
    @commands.has_permissions(ban_members=True)
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        embed = (
            discord.Embed(
                title=f'Role Information: {str(role)}', 
                color=accent_color
            )
        ).add_field(
            name='Creation Date:', 
            value=role.created_at.strftime("%b %d, %Y")
        ).add_field(
            name='Mentionable', 
            value=role.mentionable
        ).add_field(
            name='Managed By Integration', 
            value=role.is_integration()
        ).add_field(
            name='Managed By Bot', 
            value=role.is_bot_managed()
        ).add_field(
            name='Role Position', 
            value=role.position
        ).add_field(
            name='Role ID', 
            value=f'`{role.id}`'
        ).set_footer(
            text=generate_random_footer(),
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='audit', 
        help='Views the latest entries of the audit log in detail (limited to 100 entries).'
    )
    @commands.has_permissions(ban_members=True)
    async def audit(self, ctx: commands.Context, audit_limit: int):
        if int(audit_limit) > 100:
            await ctx.send('Cannot send audit log entries more than 100 at a time!')

        else:
            embed = (
                discord.Embed(
                    title='Audit Log', 
                    description=f'Showing the latest {audit_limit} entries that were made in the audit log of {ctx.guild.name}.', 
                    color=accent_color
                ).set_footer(
                    text=generate_random_footer(), 
                    icon_url=ctx.author.avatar_url
                )
            )
            async for audit_entry in ctx.guild.audit_logs(limit=audit_limit):
                embed.add_field(
                    name=f'- {audit_entry.action}', 
                    value=f'User: {audit_entry.user} | Target: {audit_entry.target}', 
                    inline=False
                )
            await ctx.send(embed=embed)


# Moderation category commands.
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='purge', 
        help='Clears messages within the given index.'
    )
    @commands.has_permissions(ban_members=True)
    async def purge(self, ctx: commands.Context, amount=1):
        if amount > 200:
            await ctx.send('Purges are limited to 200 messages per use!')
        else:
            amount += 1
            await ctx.channel.purge(limit=amount)

    @commands.command(
        name='ripplepurge', 
        help='Clears messages that are sent by a specific user within the given index.'
    )
    @commands.has_permissions(ban_members=True)
    async def ripplepurge(self, ctx: commands.Context, member: discord.Member, amount=2):
        if amount > 100:
            await ctx.send('Ripple purges are limited to 100 messages per use!')
        else:
            await ctx.message.add_reaction('✅')
            messages = await ctx.history(limit=amount).flatten()

            for message in messages:
                if message.author == member:
                    await message.delete()

    @commands.command(
        name='msgweb', 
        help='Enables a web trap to capture six messages sent by a specific user.'
    )
    @commands.has_permissions(ban_members=True)
    async def msgweb(self, ctx: commands.Context, member: discord.Member):
        global msg_web_target

        if not msg_web_target:
            msg_web_target.append([member, ctx.author])
            await ctx.author.send(f'A message web trap on {member.name} has been triggered. The captured messages will be delivered to you shortly after the web has completed it\'s task.')
            await ctx.message.delete()

        else:
            await ctx.author.send('Something fishy is already going on. Try again later!')
            await ctx.message.delete()

    @commands.command(
        name='snipemsg',
        help='Snipes a recent message from the channel.'
    )
    @commands.has_permissions(ban_members=True)
    async def snipemsg(self, ctx: commands.Context):
        if snipeables:
            for snipeable in snipeables:
                if snipeable.guild == ctx.guild:
                    webhook = await ctx.message.channel.create_webhook(name=snipeable.author.name)
                    await webhook.send(snipeable.content, username=snipeable.author.name, avatar_url=snipeable.author.avatar_url)
                    await webhook.delete()
                    snipeables.remove(snipeable)

        else:
            await ctx.send('No messages were found in my list.')

    @commands.command(
        name='jail', 
        help='Temporarily prevents a member from chatting in server.'
    )
    @commands.has_permissions(ban_members=True)
    async def jail(self, ctx: commands.Context, member: discord.Member, *, reason='No reason provided.'):
        do_jail = False

        if member != self.bot.user:
            if member != ctx.author:
                if member.guild_permissions.administrator:
                    if ctx.author.guild_permissions.administrator:
                        do_jail = True
                    else:
                        await ctx.send('You can\'t jail an admin!')
                else:
                    do_jail = True
            else:
                await ctx.send('You can\'t jail yourself!')
        else:
            await ctx.send('Why are you even trying to jail me?')

        if do_jail:
            jail_members.append([member, ctx.guild, reason, ctx.author])
            await ctx.message.delete()
            await ctx.send(f'You\'ve been captured! {member.mention} | Reason: {reason}')

    @commands.command(
        name='jailed', 
        help='Views jailed members.'
    )
    @commands.has_permissions(ban_members=True)
    async def jailed(self, ctx: commands.Context):
        jail_has_member = False
        embed = (
            discord.Embed(
                title='Now viewing the prison!', 
                color=accent_color
            ).set_footer(
                icon_url=ctx.author.avatar_url, 
                text=generate_random_footer()
            )
        )
        for jail_member in jail_members:
            if jail_member[1] == ctx.guild:
                embed.add_field(
                    name=jail_member[0].name, 
                    value=('Jailed by ' + jail_member[3].mention + ' | Reason: `' + jail_member[2] + '`'), 
                    inline=False
                )
                jail_has_member = True

        if jail_has_member is False:
            await ctx.send('No members are inside the jail.')

        else:
            await ctx.send(embed=embed)

    @commands.command(
        name='unjail', 
        help='Removes a member from jail.'
    )
    @commands.has_permissions(ban_members=True)
    async def unjail(self, ctx: commands.Context, member: discord.Member):
        for jail_member in jail_members:
            if jail_member[1] == ctx.guild and jail_member[0] == member:
                if member != ctx.author:
                    jail_members.remove(jail_member)
                    await ctx.message.add_reaction('✅')

                else:
                    await ctx.send('You can\'t free yourself!')

    @commands.command(
        name='block', 
        help='Blocks a user from chatting in a specific channel.'
    )
    @commands.has_permissions(ban_members=True)
    async def block(self, ctx: commands.Context, member: discord.Member, *, reason='No reason provided.'):
        if member != self.bot.user:
            if member != ctx.author:
                await ctx.channel.set_permissions(member, send_messages=False)
                await ctx.message.delete()
                await ctx.send(f'You\'re now blocked from chatting, {member.mention} | Reason: {reason}')

            else:
                await ctx.send(f'You can\'t block yourself!')
        else:
            await ctx.send(f'Why are you even trying to block me?')

    @commands.command(
        name='unblock', 
        help='Unblocks a user.'
    )
    @commands.has_permissions(ban_members=True)
    async def unblock(self, ctx: commands.Context, member: discord.Member):
        await ctx.channel.set_permissions(member, overwrite=None)
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='kick', 
        help='Kicks a member from server.'
    )
    @commands.has_permissions(ban_members=True)
    async def kick(self, ctx: commands.Context, member: discord.User, *, reason='No reason provided.'):
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f'Member **{member.name}** has been kicked! Reason: {reason}')
        await ctx.message.delete()

    @commands.command(
        name='ban', 
        help='Bans a member from server.'
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.User, *, reason='No reason provided.'):
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f'Member **{member.name}** has been banned! Reason: {reason}')
        await ctx.message.delete()

    @commands.command(
        name='bans', 
        help='Shows a list of banned users in the server.'
    )
    @commands.has_permissions(ban_members=True)
    async def bans(self, ctx: commands.Context):
        bans = await ctx.guild.bans()
        embed = (
            discord.Embed(
                title='Now viewing banned members!', 
                color=accent_color
            ).set_footer(
                icon_url=ctx.author.avatar_url, 
                text=generate_random_footer()
            )
        )
        if bans:
            for ban in bans:
                embed.add_field(
                    name=ban.user, 
                    value=f'ID: `{ban.user.id}` | Reason: `{ban.reason}`', 
                    inline=False
                )
            await ctx.send(embed=embed)

        else:
            await ctx.send('No members are banned from this server.')

    @commands.command(
        name='unban', 
        help='Unbans a member in server.'
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, member: discord.User):
        await ctx.guild.unban(member)
        await ctx.send(f'Member **{member.name}** has been unbanned!')

    @commands.command(
        name='freeze', 
        help='Calms down chat.'
    )
    @commands.has_permissions(ban_members=True)
    async def freeze(self, ctx: commands.Context):
        frozen_guilds.append([ctx.author, ctx.guild, ctx.message.channel])
        await ctx.message.delete()
        await ctx.send(f'**Chat was frozen by {ctx.author.mention}!**')

    @commands.command(
        name='thaw', 
        help='Removes frozen state from chat.'
    )
    @commands.has_permissions(ban_members=True)
    async def thaw(self, ctx: commands.Context):
        for frozen_guild in frozen_guilds:
            if frozen_guild[1] == ctx.guild:
                frozen_guilds.remove(frozen_guild)
                await ctx.message.add_reaction('✅')

class meme(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name='meme', 
        help='sends random memes straight from reddit'
    )
    async def meme(self, ctx):
        async with ctx.channel.typing():
            sub = random.choice(["memes", "dankmemes"])
            subreddit = reddit.subreddit(f"{sub}")
            memes = []
            for submission in subreddit.hot(limit=100):
                if not submission.stickied:
                    memes.append(submission)

            choice = random.choice(range(len(memes)))
            title = memes[choice].title
            url = memes[choice].url
            permalink = memes[choice].permalink
            embed = discord.Embed(
                colour=0x2859B8,
                description=f"**[{title}](https://www.reddit.com{permalink})**",
            )
            embed.set_image(url=f"{url}")
        await ctx.send(embed=embed)

# Customization category commands.
class Customization(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='makeinv', 
        help='Creates an invite code or link.'
    )
    @commands.has_permissions(ban_members=True)
    async def makeinv(self, ctx: commands.Context, max_age=60, max_uses=1, *, reason='No reason provided.'):
        if not reason:
            reason = f'Inviter: {ctx.author.name}'

        invite = await ctx.channel.create_invite(max_age=max_age, max_uses=max_uses, reason=reason)
        embed = (
            discord.Embed(
                color=accent_color
            ).add_field(
                name='Link', 
                value=invite
            ).add_field(
                name='ID', 
                value=f'`{invite.id}`'
            ).add_field(
                name='Channel', 
                value=invite.channel
            ).set_author(
                name='An invite was created!', 
                icon_url=ctx.author.avatar_url
            )
        )

        value = str()
        if invite.max_age == 0:
            value = 'Infinity'
        else:
            value = f'{invite.max_age} Seconds'

        embed.add_field(
            name='Lifetime', 
            value=value
        ).add_field(
            name='Max Uses', 
            value=invite.max_uses
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='invites', 
        help='Shows all active server invite codes.'
    )
    @commands.has_permissions(ban_members=True)
    async def invites(self, ctx: commands.Context):
        invites = await ctx.guild.invites()
        embed = (
            discord.Embed(
                title='Now viewing invite codes!', 
                color=accent_color
            ).set_footer(
                icon_url=ctx.author.avatar_url, 
                text=generate_random_footer()
            )
        )

        if not invites:
            await ctx.send('No invite codes have been generated.')

        else:
            invcount = 0
            for invite in invites:
                invcount += 1
                embed.add_field(
                    name=invite, 
                    value=f'Uses: {invite.uses} | Inviter: {invite.inviter.name} | ID: `{invite.id}`', 
                    inline=False
                )
            await ctx.send(embed=embed)

    @commands.command(
        name='removeinv', 
        help='Removes a previously generated invite code or link.'
    )
    @commands.has_permissions(ban_members=True)
    async def removeinv(self, ctx: commands.Context, invite_id):
        invites = await ctx.guild.invites()
        for invite in invites:
            if invite.id == invite_id:
                await invite.delete()
                await ctx.send('Invite has been deleted.')
                
    @commands.command(
        name='makerole', 
        help='Creates a role.'
    )
    @commands.has_permissions(ban_members=True)
    async def makerole(self, ctx: commands.Context, *, role):
        await ctx.guild.create_role(name=role)
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='removerole', 
        help='Removes an existing role.'
    )
    @commands.has_permissions(ban_members=True)
    async def removerole(self, ctx: commands.Context, *, role: discord.Role):
        if role is None:
            await ctx.send('That\'s not a role, I guess?')

        else:
            await role.delete()
            await ctx.message.add_reaction('✅')

    @commands.command(
        name='assignrole', 
        help='Assigns an existing role to a server member.', pass_context=True
    )
    @commands.has_permissions(ban_members=True)
    async def assignrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await member.add_roles(role)
        await ctx.send(f'Role {role.mention} has been given to {member.mention}, peace! :partying_face:')

    @commands.command(
        name='makech', 
        help='Creates a server channel.'
    )
    @commands.has_permissions(ban_members=True)
    async def makech(self, ctx: commands.Context, *, channel_name):
        guild = ctx.guild
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if not existing_channel:
            await guild.create_text_channel(channel_name)
            await ctx.message.add_reaction('✅')

    @commands.command(
        name='removech', 
        help='Removes an existing server channel.'
    )
    @commands.has_permissions(ban_members=True)
    async def removech(self, ctx: commands.Context, channel_name: discord.TextChannel):
        await channel_name.delete()
        await ctx.message.add_reaction('✅')


# Music category commands.
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return "**{0.title}** by **{0.uploader}**".format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(
                'Couldn\'t find anything that matches **{}**'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(
                    'Couldn\'t find anything that matches **{}**'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(
            cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch **{}**'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(
                        'Couldn\'t retrieve any matches for **{}**'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (
            discord.Embed(
                title='Now vibin\' to:',
                description='```css\n{0.source.title}\n```'.format(self),
                color=accent_color
            ).add_field(
                name='Duration', 
                value=self.source.duration
            ).add_field(
                name='Requested by', 
                value=self.requester.mention
            ).add_field(
                name='Uploader', 
                value='[{0.source.uploader}]({0.source.uploader_url})'.format(self)
            ).add_field(
                name='URL', 
                value='[Click here to redirect]({0.source.url})'.format(self)
            ).set_thumbnail(
                url=self.source.thumbnail
            )
        )
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None

            if self.loop == False:
                try:
                    async with timeout(180):
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return
                
                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)

            elif self.loop == True:
                self.now = discord.FFmpegPCMAudio(self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS)
                self.voice.play(self.now, after=self.play_next_song)
            
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                'Sorry, this command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Whoops! {}'.format(str(error)))

    @commands.command(
        name='join', 
        help='Joins a specific voice channel.', 
        invoke_without_subcommand=True
    )
    async def _join(self, ctx: commands.Context):
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        await ctx.message.add_reaction('✅')
        ctx.voice_state.voice = await destination.connect()

    @commands.command(
        name='summon', 
        help='Summons bot to a particular voice channel.'
    )
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        if not channel and not ctx.author.voice:
            raise VoiceError(
                'You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='leave', 
        help='Clears the queue and leaves the voice channel.'
    )
    async def _leave(self, ctx: commands.Context):
        if not ctx.voice_state.voice:
            return await ctx.send('I am not connected to any voice channel.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='volume', 
        help='Sets the volume of the player.'
    )
    async def _volume(self, ctx: commands.Context, *, volume: int):
        if not ctx.voice_state.is_playing:
                return await ctx.send('There\'s nothing being played at the moment.')

        if 0 >= volume >= 100:
                return await ctx.send('Volume must be between 0 and 100 to execute the command.')

        ctx.voice_state.current.source.volume = volume / 100
        await ctx.send('Volume of the player is now set to **{}%**'.format(volume))


    @commands.command(
        name='now', 
        help='Displays the currently playing song.'
    )
    async def _now(self, ctx: commands.Context):
        try:
            await ctx.send(embed=ctx.voice_state.current.create_embed())
        except AttributeError:
            await ctx.send('There\'s nothing being played at the moment.')

    @commands.command(
        name='pause', 
        help='Pauses the currently playing song.'
    )
    async def _pause(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('✅')

    @commands.command(
        name='resume', 
        help='Resumes a currently paused song.'
    )
    async def _resume(self, ctx: commands.Context):
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('✅')

    @commands.command(
        name='stop', 
        help='Stops playing song and clears the queue.'
    )
    async def _stop(self, ctx: commands.Context):
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('✅')

    @commands.command(
        name='skip', 
        help='Vote to skip a song. The requester can automatically skip.'
    )
    async def _skip(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('Not playing any music right now, so no skipping for you.')

        voter = ctx.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('✅')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('✅')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3** votes.'.format(total_votes))

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(
        name='queue', 
        help='Shows the player\'s queue.'
    )
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Empty queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(
                i + 1, song)

        embed = (
            discord.Embed(
                description='**{} tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue)
            ).set_footer(
                text='Viewing page {}/{}'.format(page, pages)
            )
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='shuffle', 
        help='Shuffles the queue.'
    )
    async def _shuffle(self, ctx: commands.Context):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('The queue is empty, play some songs, maybe?')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='remove',
        help='Removes a song from the queue at a given index.'
    )
    async def _remove(self, ctx: commands.Context, index: int):
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('The queue is empty, so nothing to be removed.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='loop', 
        help='Loops the currently playing song.'
    )
    async def _loop(self, ctx: commands.Context):
        if not ctx.voice_state.is_playing:
            return await ctx.send('There\'s nothing being played at the moment.')

        ctx.voice_state.loop = not ctx.voice_state.loop
        if ctx.voice_state.loop:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❎')

    @commands.command(
        name='play', 
        help='Plays a song.'
    )
    async def _play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('Whoops! An error occurred while processing this request: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Enqueued {} for the jam!'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError(
                'You are not connected to any voice channel.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('I\'m already in a voice channel.')


# Developer commands/tools.
class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='togglekeepalive',
        help='Toggles the optional support layer for keeping the system alive.'
    )
    async def togglekeepalive(self, ctx: commands.Context):
        global keep_alive_toggle
        keep_alive_toggle = not keep_alive_toggle
        await ctx.send(f'Keep alive has been toggled to `{keep_alive_toggle}`!')

    @commands.command(
        name='logout', 
        help='Logs out from the system.'
    )
    async def logout(self, ctx: commands.Context):
        if developer_check(ctx.author.id):
            print('Log: Signing out of the system.')
            await ctx.message.add_reaction('✅')
            await self.bot.close()




keep_alive()


# Add available cogs.
bot.add_cog(ExceptionHandler(bot))
bot.add_cog(Chill(bot))
bot.add_cog(Inspection(bot))
bot.add_cog(Moderation(bot))
bot.add_cog(Customization(bot))
bot.add_cog(Music(bot))
bot.add_cog(Developer(bot))


# Run the bot.
bot.run(token)