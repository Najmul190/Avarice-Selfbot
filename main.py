import base64, discord, json, asyncio, aiohttp, requests, os, sys, uuid, datetime, random, codecs, threading, time as t

from colorama import init, Fore, Style
from data.model.imaginepy import AsyncImagine, Style, Ratio
from discord import SyncWebhook
from discord.ext import commands
from datetime import timedelta

with open("config.json", "r") as cjson:
    config = json.load(cjson)


######################################### Console #########################################

currentVersion = "1.0.0"

init(autoreset=True)


def check_version():
    try:
        version = requests.get(
            "https://raw.githubusercontent.com/Najmul190/Avarice-Selfbot/main/version.txt"
        )

        if version.text != currentVersion:
            changes = requests.get(
                "https://raw.githubusercontent.com/Najmul190/Avarice-Selfbot/main/data/changelog.txt"
            )

            if "REQUIRED" in changes.text:
                print(
                    f"{Fore.RED}There is a required update on the GitHub, you must update to continue using Avarice: {Fore.RESET}https://github.com/Najmul190/Avarice-Selfbot\n\nChangelog:\n{changes.text}"
                )

                input("\nPress enter to exit...")
                os._exit(0)

            else:
                print(
                    f"{Fore.YELLOW}This version is outdated. Please update to version {Fore.WHITE}{version.text} {Fore.YELLOW}from {Fore.RESET}https://github.com/Najmul190/Avarice-Selfbot\n\nChangelog:\n{changes.text}\n"
                )
    except:
        pass


if os.name == "nt":
    os.system("cls")
else:
    os.system("clear")

startTime = datetime.datetime.utcnow()


def title():
    while True:
        uptime = datetime.datetime.utcnow() - startTime
        days, hours, minutes, seconds = (
            uptime.days,
            uptime.seconds // 3600,
            (uptime.seconds // 60) % 60,
            uptime.seconds % 60,
        )
        if days >= 1:
            time_str = f"{days}f:{hours:02}:{minutes:02}:{seconds:02}"
        else:
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        os.system(f"title Avarice Selfbot - {time_str}")
        t.sleep(1)


if os.name == "nt":
    threading.Thread(target=title).start()


text = f"""
                                 █████╗ ██╗   ██╗ █████╗ ██████╗ ██╗ ██████╗███████╗
                                ██╔══██╗██║   ██║██╔══██╗██╔══██╗██║██╔════╝██╔════╝
                                ███████║██║   ██║███████║██████╔╝██║██║     █████╗
                                ██╔══██║╚██╗ ██╔╝██╔══██║██╔══██╗██║██║     ██╔══╝
                                ██║  ██║ ╚████╔╝ ██║  ██║██║  ██║██║╚██████╗███████╗
                                ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝ 1.0.0"""


print(text)
credits = """                                                     by Najmul190"""
print(credits)
print("")
line = "-" * 120
print(line)
print("")

# pretty ugly for now but rgbprint didnt work on other systems and i wanted a cool gradient :(

if config["token"] == "":
    TOKEN = input(
        "Looks like you haven't entered your token yet, please enter it now: "
    )

    config["token"] = TOKEN

    with open("config.json", "w") as cjson:
        json.dump(config, cjson, indent=4)

    print(Fore.GREEN + "Token successfully saved.")

    PREFIX = input("What would you like the prefix to be? (Default: >) ")

    if PREFIX == "":
        print(Fore.GREEN + "Successfully setup Avarice. Starting...")

    else:
        config["prefix"] = PREFIX

        with open("config.json", "w") as cjson:
            json.dump(config, cjson, indent=4)

    print(
        Fore.GREEN
        + "Prefix successfully set to: "
        + config["prefix"]
        + ". Starting Avarice..."
    )

    os.execl(sys.executable, sys.executable, *sys.argv)


check_version()


####################################### Initialisation ####################################


bot = commands.Bot(
    command_prefix=config["prefix"], self_bot=True, case_insensitive=True
)


pingMute = False
pingKick = False
pingRole = None

pinSpam = None

mimic = None
smartMimic = None

reactUser = None
reactEmoji = None
blockReaction = None

deleteAnnoy = None
forceDisconnect = None

afkMode = False
afkLogs = []

whitelist = []
messageLogsBlacklist = []

noLeave = []
forcedNicks = {}

spyList = []
notifyWords = []


def load_config():
    with open("data/webhooks.txt", "r") as file:
        webhook_lines = file.read().splitlines()

    if webhook_lines == []:
        return

    webhooks = {}

    for line in webhook_lines:
        key, url = line.split(": ")
        webhooks[key.strip()] = url.strip()

    global spyWebhook
    spyWebhook = webhooks["Spy"]

    global ticketsWebhook
    ticketsWebhook = webhooks["Tickets"]

    global messageLogsWebhook
    messageLogsWebhook = webhooks["Message Logs"]

    global relationshipLogsWebhook
    relationshipLogsWebhook = webhooks["Relationship Logs"]

    global guildLogsWebhook
    guildLogsWebhook = webhooks["Guild Logs"]

    global roleLogsWebhook
    roleLogsWebhook = webhooks["Role Logs"]

    global pingLogsWebhook
    pingLogsWebhook = webhooks["Ping Logs"]

    global wordNotifications
    wordNotifications = webhooks["Word Notifications"]

    global pingLogs
    pingLogs = webhooks["Ping Logs"]

    global ghostpingLogsWebhook
    ghostpingLogsWebhook = webhooks["Ghostping Logs"]

    with open("data/logsblacklist.txt", "r") as file:
        blacklisted = file.readlines()

    blacklisted = [number.strip() for number in blacklisted]

    for channelid in blacklisted:
        try:
            messageLogsBlacklist.append(int(channelid))
        except:
            pass

    if config["notificationWords"] != [""]:
        for word in config["notificationWords"]:
            notifyWords.append(word)


load_config()


@bot.event
async def on_ready():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    print(
        f"""{current_time} | {Fore.GREEN}Connected to: {Fore.RESET}{bot.user.name}#{bot.user.discriminator} ({bot.user.id})
           {Fore.GREEN}Prefix: {Fore.RESET}{config["prefix"]}     {Fore.GREEN}Total Servers: {Fore.RESET}{len(bot.guilds)}     {Fore.GREEN}Total Friends: {Fore.RESET}{len(bot.friends)}\n"""
    )

    requests.post(
        "https://avariceapi.najmul190.repl.co/api/user",
        data={
            "username": f"{bot.user.id}"
        },  # this is just for my own statistics, nothing malicious
    )

    if config["webhooks"] == "True" and os.stat("data/webhooks.txt").st_size == 0:
        print(
            f"{current_time} | {Fore.YELLOW}Looks like you haven't setup your webhooks yet, but you have webhooks enabled in the config. Please run {Fore.RESET}{config['prefix']}setupwebhooks {Fore.YELLOW}to do so."
        )


def log_message(command, message, color=Fore.WHITE):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    if " " in command:
        log = f"{current_time} | {Fore.WHITE}{command}{Fore.RESET} | {color}{message}"
    else:
        log = f'{current_time} | {Fore.BLUE}{config["prefix"]}{command}{Fore.RESET} | {color}{message}'

    print(log)


def log_webhook(webhook, content=None, type=None):
    if config["webhooks"] == False:
        return

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    current_date = datetime.datetime.now().strftime("%d/%m/%y")

    data = {
        "embeds": [
            {
                "title": f"Avarice {type} Logs",
                "description": f"{content}",
                "color": 1123464,
                "footer": {"text": f"Avarice • {current_time} on {current_date}"},
                "thumbnail": {
                    "url": "https://media.discordapp.net/attachments/980478553583931432/1116861500129284206/a_1b8acca6bb720b7a5a53c7f0c1820a3e.gif"
                },
            }
        ],
        "username": f"Avarice {type} Logs",
        "avatar_url": "https://media.discordapp.net/attachments/980478553583931432/1116861500129284206/a_1b8acca6bb720b7a5a53c7f0c1820a3e.gif",
    }

    webhook = SyncWebhook.from_url(webhook)
    webhook.send(embeds=[discord.Embed.from_dict(embed) for embed in data["embeds"]])


@bot.event
async def on_message(message):
    if message.author != bot.user:
        for word in notifyWords:
            if word in message.content.lower():
                try:
                    index = message.content.lower().index(word)
                    messageContent = (
                        message.content[:index]
                        + f"`{message.content[index:index+len(word)]}`"
                        + message.content[index + len(word) :]
                    )

                    log_webhook(
                        wordNotifications,
                        f"**{message.author.name}** said `{word}` in {message.jump_url}\n\n{messageContent}",
                        "Word Notifications",
                    )

                    index = message.content.lower().index(word)
                    messageContent = (
                        message.content[:index]
                        + f"[{message.content[index:index+len(word)]}]"
                        + message.content[index + len(word) :]
                    )

                    log_message(
                        "Word Notifications",
                        f"{message.guild.name}: {message.channel.name} | {message.author.name}: {messageContent}",
                        Fore.YELLOW,
                    )
                except:
                    pass
    if (
        pingMute == True
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if bot.user.mentioned_in(message):
            try:
                await message.author.timeout(timedelta(seconds=600))
                log_message(
                    "pingmute",
                    f"Muted {message.author.name} for 10 minutes for pinging you.",
                )
            except:
                pass
    if (
        pingKick == True
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if bot.user.mentioned_in(message):
            try:
                await message.author.kick()
                log_message(
                    "pingkick", f"Kicked {message.author.name} for pinging you."
                )
            except:
                pass
    if (
        pingRole != None
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if bot.user.mentioned_in(message):
            try:
                await message.author.add_roles(pingRole)
                log_message(
                    "pingrole",
                    f"Gave {message.author.name} the role {pingRole.name} for pinging user.",
                )
            except:
                pass
    if (
        config["webhooks"] == "True"
        and config["pingLogs"] == "True"
        and bot.user.mentioned_in(message)
    ):
        message.content = message.content.replace(
            f"<@{bot.user.id}>", f"@{bot.user.name}"
        )

        log_webhook(
            pingLogsWebhook,
            f"{message.author.mention} pinged you in {message.channel.mention}.\nMessage:\n{message.content}",
            "Ping",
        )

        log_message(
            "Ping Logs",
            f"{message.author.name} pinged you in #{message.channel.name}. Message: {message.content}",
            Fore.YELLOW,
        )
    if (
        mimic == message.author
        and message.author != bot.user
        and message.guild.id not in whitelist
        and not message.content.startswith(config["prefix"])
    ):
        await message.channel.send(message.content)

    if (
        smartMimic == message.author
        and message.author != bot.user
        and message.guild.id not in whitelist
        and not message.content.startswith(config["prefix"])
    ):
        mocked_text = "".join(
            char.upper() if i % 2 == 0 else char.lower()
            for i, char in enumerate(message.content)
        )

        await message.channel.send(mocked_text)
    if (
        pinSpam != None
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if message.author == pinSpam:
            try:
                await message.pin()
            except:
                pass

    if (
        deleteAnnoy != None
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if message.author == deleteAnnoy:
            try:
                await message.delete()

                log_message(
                    "deleteannoy",
                    f"Deleted {message.author.name}'s message: {message.content}",
                )
            except:
                pass

    if (
        reactUser != None
        and message.author != bot.user
        and message.guild.id not in whitelist
    ):
        if message.author == reactUser:
            try:
                await message.add_reaction(reactEmoji)
            except:
                pass

    if afkMode == True:
        if message.author != bot.user:
            if message.author.id not in afkLogs:
                if message.channel.type == discord.ChannelType.private:
                    await message.channel.send(config["afk_message"])

                    log_message(
                        "AFK Logs",
                        f"DM from {message.author.name}#{message.author.discriminator}: {message.content}",
                        Fore.YELLOW,
                    )

                    afkLogs.append(message.author.id)
            else:
                if message.channel.type == discord.ChannelType.private:
                    log_message(
                        "AFK Logs",
                        f"{message.author.name}#{message.author.discriminator}: {message.content}",
                        Fore.YELLOW,
                    )
        else:
            await bot.process_commands(message)
    else:
        if message.author == bot.user:
            await bot.process_commands(message)


async def delete_after_timeout(message):
    await asyncio.sleep(config["delete_timeout"])
    await message.delete()


@bot.event
async def on_reaction_add(reaction, user):
    if blockReaction is not None:
        if reaction.emoji == blockReaction:
            if user.id != bot.user.id:
                try:
                    await reaction.remove(user)

                    log_message(
                        "blockreaction",
                        f"Removed {user.name}'s reaction from the block reaction message.",
                    )
                except:
                    pass


@bot.event
async def on_group_remove(ctx, member):
    if member.id in noLeave:
        await ctx.add_recipients(member)
        log_message("noleave", f"{member.name} has been added back to the group.")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel == None:
        if forceDisconnect != None:
            if member == forceDisconnect:
                try:
                    await member.edit(voice_channel=None)

                    log_message(
                        "forcedisconnect",
                        f"{member.name} has been disconnected from the voice channel.",
                    )
                except:
                    pass


@bot.event
async def on_guild_channel_create(channel):
    if channel.permissions_for(channel.guild.me).read_messages:
        if "ticket" in channel.name and isinstance(channel, discord.TextChannel):
            log_message(
                "Ticket Logs",
                f"New ticket channel created in {channel.guild.name}: {channel.name}",
                Fore.GREEN,
            )

            if config["webhooks"] == "True" and config["ticketWebhook"] == "True":
                log_webhook(
                    ticketsWebhook,
                    f"New ticket channel created: <#{channel.id}>",
                    "Tickets",
                )


@bot.event
async def on_member_remove(member):
    if (
        member.id == bot.user.id
        and config["webhooks"] == "True"
        and config["guildLogs"] == "True"
    ):
        log_webhook(
            guildLogsWebhook,
            f"You've been removed from the server: {member.guild}.",
            "Guild",
        )

        log_message(
            "Guild Logs",
            f"You've been removed from the server: {member.guild}.",
            Fore.RED,
        )


@bot.event
async def on_relationship_remove(friend):
    log_message(
        "Relationship Logs",
        f"You've been removed as a friend by {friend.user.name}#{friend.user.discriminator}.",
        Fore.RED,
    )

    if config["webhooks"] == "True" and config["relationshipLogs"] == "True":
        log_webhook(
            relationshipLogsWebhook,
            f"You've been removed as a friend by {friend.user.name}#{friend.user.discriminator}.",
            "Relationship",
        )


@bot.event
async def on_member_update(before, after):
    if before.id == bot.user.id:
        if before.roles != after.roles:
            for role in after.roles:
                if role not in before.roles:
                    log_message(
                        "Role Logs",
                        f"You've been given the role {role.name} in {after.guild.name}.",
                        Fore.GREEN,
                    )

                    if config["webhooks"] == "True" and config["roleLogs"] == "True":
                        log_webhook(
                            roleLogsWebhook,
                            f"You've been given the role `{role.name}` in {after.guild.name}.",
                            "Guild",
                        )

            for role in before.roles:
                if role not in after.roles:
                    log_message(
                        "Role Logs",
                        f"You've been removed from the role {role.name} in {after.guild.name}.",
                        Fore.RED,
                    )

                    if config["webhooks"] == "True" and config["roleLogs"] == "True":
                        log_webhook(
                            roleLogsWebhook,
                            f"You've been removed from the role `{role.name}` in {after.guild.name}.",
                            "Guild",
                        )


@bot.event
async def on_user_update(before, after):
    friendsList = []

    for friend in bot.friends:
        friendsList.append(friend.id)

    if before.id in friendsList:
        if before.name != after.name:
            log_message(
                "Relationship Logs",
                f"Your friend {before.name}#{before.discriminator} has changed their name to {after.name}#{after.discriminator}.",
            )

            if config["webhooks"] == "True" and config["relationshipLogs"] == "True":
                log_webhook(
                    relationshipLogsWebhook,
                    f"Your friend `{before.name}#{before.discriminator}` has changed their name to `{after.name}#{after.discriminator}`.",
                    "Relationship",
                )

        if before.avatar != after.avatar:
            log_message(
                "Relationship Logs",
                f"Your friend {before.name}#{before.discriminator} has changed their avatar.",
            )

            if config["webhooks"] == "True" and config["relationshipLogs"] == "True":
                log_webhook(
                    relationshipLogsWebhook,
                    f"Your friend `{before.name}#{before.discriminator}` has changed their avatar.",
                    "Relationship",
                )


previous_presence = {}


@bot.event
async def on_presence_update(before, after):
    member_id = after.id

    if member_id in spyList:
        previous_activity = previous_presence.get(member_id)
        current_activity = after.activity

        if isinstance(after, discord.Member):
            current_activity = after.activity

        if previous_activity != current_activity:
            if current_activity == None:
                log_message("spy", f"{after.name} is no longer doing anything.")
                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook, f"{after.name} is no longer doing anything.", "Spy"
                    )

            elif "playing" in str(current_activity.type):
                log_message(
                    "spy",
                    f"{after.name} is now playing {current_activity.name}.",
                )

                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook,
                        f"{after.name} is now playing {current_activity.name}.",
                        "Spy",
                    )
            elif "streaming" in str(current_activity.type):
                log_message(
                    "spy",
                    f"{after.name} is now streaming {current_activity.name}.",
                )

                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook,
                        f"{after.name} is now streaming {current_activity.name}.",
                        "Spy",
                    )
            elif "listening" in str(current_activity.type):
                log_message(
                    "spy",
                    f"{after.name} is now listening to {current_activity.name}.",
                )

                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook,
                        f"{after.name} is now listening to {current_activity.name}.",
                        "Spy",
                    )
            elif "watching" in str(current_activity.type):
                log_message(
                    "spy",
                    f"{after.name} is now watching {current_activity.name}.",
                )

                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook,
                        f"{after.name} is now watching {current_activity.name}.",
                        "Spy",
                    )
            elif current_activity == "Spotify":
                log_message(
                    "spy",
                    f"{after.name} is now listening to Spotify.",
                )

                if config["webhooks"] == "True" and config["spyWebhook"] == "True":
                    log_webhook(
                        spyWebhook, f"{after.name} is now listening to Spotify.", "Spy"
                    )

        previous_presence[member_id] = current_activity


@bot.command(description="Shows the bot's ping.")
async def ping(ctx):
    if round(bot.latency * 1000) < 100:
        strength = ":white_check_mark:"
    elif round(bot.latency * 1000) > 100 and round(bot.latency * 1000) < 500:
        strength = ":warning:"
    elif round(bot.latency * 1000) > 500:
        strength = ":x:"

    await ctx.message.edit(
        content=f":ping_pong: | Bot ping: {round(bot.latency * 1000)}ms | {strength}"
    )

    log_message(
        "ping",
        f"Current ping: {round(bot.latency * 1000)}ms",
    )

    await delete_after_timeout(ctx.message)


####################################### Moderation #######################################


@bot.command(
    aliases=["textchannel", "createtextchannel"],
    description="Creates a text channel, with an optional nsfw argument. (True/False)",
)
async def createtext(ctx, name, *, nsfw=False):
    channel = await ctx.guild.create_text_channel(name=name, nsfw=nsfw)
    await ctx.message.edit(content=f"Created text channel: <#{channel.id}>")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["voicechannel", "createvoicechannel"],
    description="Creates a voice channel.",
)
async def createvoice(ctx, *, name):
    channel = await ctx.guild.create_voice_channel(name=name)
    await ctx.message.edit(content=f"Created voice channel: <#{channel.id}>")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["nickforce"],
    description="Repeatedly changes a user's nickname to the specified nickname, forcing them to keep it.",
)
async def forcenick(ctx, member: discord.Member, *, nickname):
    await ctx.message.delete()
    if member.id in forcedNicks:
        await forcedNicks[member.id].cancel()
    forcedNicks[member.id] = asyncio.create_task(change_nick(member, nickname))

    message = await ctx.send(f"Forcing {member.name} to use nickname: {nickname}")
    await delete_after_timeout(message)


async def change_nick(member, nickname):
    await member.edit(nick=nickname)

    while True:
        if member.nick == nickname:
            pass
        else:
            await member.edit(nick=nickname)

            log_message(
                "forcenick",
                f"Forced {member.name} to use nickname: {nickname}",
            )

        await asyncio.sleep(0.5)


@bot.command(
    aliases=["stopnickforce"], description="Stops forcing a user to use a nickname."
)
async def stopforcenick(ctx, member: discord.Member):
    await ctx.message.delete()

    if member.id in forcedNicks:
        forcedNicks[member.id].cancel()
        del forcedNicks[member.id]
        await ctx.send(f"Stopped forcing nickname for {member.mention}")
    else:
        await ctx.send(
            f"{member.mention} is not currently being forced to use a nickname."
        )

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["nickname"], description="Changes a user's nickname.")
async def nick(ctx, member: discord.Member, *, nickname):
    await member.edit(nick=nickname)

    await ctx.message.edit(content=f"Changed {member.name}'s nickname to {nickname}")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["clear"], description="Clears a specified amount of messages.")
async def purge(ctx, amount: int):
    await ctx.message.delete()

    try:
        deleted = await ctx.channel.purge(limit=amount)
    except discord.Forbidden:
        await ctx.send(":x: | I do not have permission to purge messages.")
        return
    except discord.HTTPException:
        await ctx.send(":x: | Failed to purge messages.")
        return

    message = await ctx.send(f"Purged {len(deleted) }messages.")
    await delete_after_timeout(message)


@bot.command(description="Clears a specified amount of messages from a specified user.")
async def purgeuser(ctx, member: discord.Member, amount: int):
    await ctx.message.delete()

    def check(message):
        return message.author == member

    try:
        deleted = await ctx.channel.purge(limit=amount, check=check)
    except discord.Forbidden:
        await ctx.send(":x: | I do not have permission to purge messages.")
        return
    except discord.HTTPException:
        await ctx.send(":x: | Failed to purge messages.")
        return

    message = await ctx.send(f"Purged {len(deleted)} messages from {member.name}.")

    log_message("purgeuser", f"Purged {len(deleted)} messages from {member.name}.")

    await delete_after_timeout(message)


@bot.command(
    description="Clears a specified amount of messages that contain a specified string."
)
async def purgecontains(ctx, amount: int, *, string):
    await ctx.message.delete()

    def check(message):
        return string in message.content

    try:
        deleted = await ctx.channel.purge(limit=amount, check=check)
    except discord.Forbidden:
        await ctx.send(":x: | I do not have permission to purge messages.")
        return
    except discord.HTTPException:
        await ctx.send(":x: | Failed to purge messages.")
        return

    message = await ctx.send(f"Purged {len(deleted)} messages that said `{string}`.")

    log_message(
        "purgecontains", f"Purged {len(deleted)} messages that said `{string}`."
    )

    await delete_after_timeout(message)


@bot.command(
    description="Clears a specified amount of messages sent by the selfbot user."
)
async def clean(ctx, amount: int = None):
    await ctx.message.delete()

    def check(message):
        return message.author == bot.user

    if amount is None:
        amount = 100

    try:
        deleted = await ctx.channel.purge(limit=amount, check=check)
    except discord.HTTPException:
        await ctx.send(":x: | Failed to purge messages.")
        return

    log_message("clean", f"Purged {len(deleted)} messages sent by me.")


@bot.command(description="Kicks the specified user.")
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.message.delete()
    await member.kick(reason=reason)

    message = await ctx.send(f"Kicked {member.mention} for {reason}")
    await delete_after_timeout(message)


@bot.command(description="Bans the specified user.")
async def ban(ctx, user, reason=None):
    await ctx.message.delete()

    if user.startswith("<@") and user.endswith(">"):
        user_id = user[3:-1]
    else:
        user_id = "".join(c for c in user if c.isdigit())

    banned_user = await bot.fetch_user(user_id)

    if banned_user is not None:
        try:
            await ctx.guild.ban(banned_user, reason=reason)
            message = await ctx.send(
                f"Banned user: {banned_user.name}#{banned_user.discriminator} ({banned_user.id})"
            )

            log_message(
                "ban",
                f"Banned user: {banned_user.name}#{banned_user.discriminator} ({banned_user.id})",
            )
        except discord.Forbidden:
            message = await ctx.send(
                "I don't have sufficient permissions to ban this user."
            )
    else:
        message = await ctx.send("Unable to find the user to ban.")

    await delete_after_timeout(message)


@bot.command(description="Unbans the specified user.")
async def unban(ctx, id: int):
    await ctx.message.delete()
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)

    message = await ctx.send(f"Unbanned {user.name}#{user.discriminator} ({user.id})")

    log_message(
        "unban",
        f"Unbanned {user.name}#{user.discriminator} ({user.id})",
    )
    await delete_after_timeout(message)


@bot.command(
    aliases=["savebans"], description="Saves all bans to a file to import later."
)
async def exportbans(ctx):
    await ctx.message.delete()

    bans = []

    async for ban in ctx.guild.bans():
        bans.append(ban)

    with open(f"data/bans_{ctx.guild.id}.txt", "w") as f:
        for ban in bans:
            f.write(f"{ban.user.id}\n")

    temp = await ctx.send(":white_check_mark: | Bans successfully saved.")

    log_message("exportbans", "Bans successfully saved.", Fore.GREEN)

    await delete_after_timeout(temp)


@bot.command(description="Imports bans from a file.")
async def importbans(ctx, guildID: int = None):
    await ctx.message.delete()

    if guildID is None:
        await ctx.send(":x: | Please specify a guild id.")
        return

    try:
        with open(f"data/bans_{guildID}.txt", "r") as f:
            bans = f.read().splitlines()
    except FileNotFoundError:
        await ctx.send(
            ":x: | Bans file not found, please make sure you have exported bans from the target guild and have used the correct guild id."
        )
        return

    for ban in bans:
        user = await bot.fetch_user(ban)
        try:
            await ctx.guild.ban(user)
        except:
            pass

    temp = await ctx.send(":white_check_mark: | Bans successfully imported.")

    log_message("importbans", "Bans successfully imported.", Fore.GREEN)

    await delete_after_timeout(temp)


@bot.command(aliases=["mute"], description="Mutes the specified user.")
async def timeout(ctx, member: discord.Member, duration: int):
    await ctx.message.delete()

    await member.timeout(timedelta(seconds=duration))

    message = await ctx.send(f"Timed out {member.mention} for {duration} seconds.")

    log_message(
        "timeout",
        f"Timed out {member.name}#{member.discriminator} ({member.id}) for {duration} seconds.",
    )

    await delete_after_timeout(message)


@bot.command(aliases=["unmute"], description="Unmutes the specified user.")
async def untimeout(ctx, member: discord.Member):
    await ctx.message.delete()

    await member.timeout(None)

    message = await ctx.send(f"Untimed out {member.mention}.")

    log_message(
        "untimeout",
        f"Untimed out {member.name}#{member.discriminator} ({member.id}).",
    )

    await delete_after_timeout(message)


@bot.command(description="Sets the slowmode of the channel in seconds.")
async def slowmode(ctx, seconds: int):
    await ctx.message.delete()

    await ctx.channel.edit(slowmode_delay=seconds)

    message = await ctx.send(f"Set slowmode to {seconds} seconds.")

    log_message(
        "slowmode",
        f"Set slowmode to {seconds} seconds.",
    )

    await delete_after_timeout(message)


@bot.command(description="Nukes a channel, cloning it and deleting the old one.")
async def nuke(ctx):
    await ctx.message.delete()

    newChannel = await ctx.channel.clone()
    await ctx.channel.delete()

    message = await newChannel.send(
        "https://gifdb.com/images/file/nuclear-explosion-slow-motion-unqdb9ho1992lida.gif"
    )

    await delete_after_timeout(message)


@bot.command(description="Gives everyone the specified role.")
async def roleall(ctx, role: discord.Role):
    await ctx.message.delete()

    for member in ctx.guild.members:
        try:
            await member.add_roles(role)
        except:
            pass

        await asyncio.sleep(0.5)

    message = await ctx.send(f"Gave everyone the role: {role.name}")

    log_message(
        "roleall",
        f"Gave everyone the role: {role.name}",
    )

    await delete_after_timeout(message)


@bot.command(description="Removes the specified role from everyone.")
async def removeroleall(ctx, role: discord.Role):
    await ctx.message.delete()

    for member in ctx.guild.members:
        try:
            await member.remove_roles(role)
        except:
            pass

        await asyncio.sleep(0.5)

    message = await ctx.send(f"Removed the role: {role.name} from everyone")

    log_message(
        "removeroleall",
        f"Removed the role: {role.name} from everyone",
    )

    await delete_after_timeout(message)


@bot.command(description="Gives the specified user all the roles in the server.")
async def giveallroles(ctx, member: discord.Member):
    await ctx.message.delete()

    for role in ctx.guild.roles:
        try:
            await member.add_roles(role)
        except:
            pass

        await asyncio.sleep(0.5)

    message = await ctx.send(f"Gave {member.mention} all the roles in the server")

    log_message(
        "giveallroles",
        f"Gave {member.name}#{member.discriminator} ({member.id}) all the roles in the server",
    )

    await delete_after_timeout(message)


########################################  Utilities ##########################################


@bot.command(description="DM's a user your token from the config file.")
async def dmtoken(ctx, user: discord.User):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.message.edit(
        content=f"Are you sure you want to DM {user.name}#{user.discriminator} with your token? (y/n)"
    )

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content="Timed out.")
        return

    if msg.content.lower() == "y":
        try:
            await user.send(config["token"])
        except Exception as e:
            await ctx.message.edit(content=f"Failed to send token: {e}")

            log_message(
                "dmtoken",
                f"Failed to send token to {user.name}#{user.discriminator} ({user.id}): {e}",
                Fore.RED,
            )

            return

        await ctx.message.edit(
            content=f"Sent token to {user.name}#{user.discriminator}."
        )

        log_message(
            "dmtoken", f"Sent token to {user.name}#{user.discriminator} ({user.id})."
        )

        await delete_after_timeout(ctx.message)

    else:
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)


@bot.command(description="Clones a server - making a new one with the same attributes.")
async def clone(ctx, server: int = None):
    if server is None:
        server = ctx.guild
        await ctx.message.delete()
    else:
        server = bot.get_guild(server)

    if server is None:
        await ctx.message.edit(content="Invalid server ID.")
        return

    await ctx.message.edit(content="Cloning server...")

    try:
        newServer = await bot.create_guild(name=server.name)

        try:
            if server.icon.url is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(server.icon.url) as resp:
                        data = await resp.read()

                await newServer.edit(icon=data)
        except:
            pass

        newServer = bot.get_guild(newServer.id)

        for channel in newServer.channels:
            await channel.delete()

        for role in reversed(server.roles):
            if role.name == "@everyone":
                continue

            await newServer.create_role(
                name=role.name,
                color=role.color,
                hoist=role.hoist,
                mentionable=role.mentionable,
                permissions=role.permissions,
            )

            await asyncio.sleep(0.5)

        for category in server.categories:
            newCategory = await newServer.create_category(
                name=category.name, position=category.position
            )

            await asyncio.sleep(0.5)

            for channel in category.channels:
                if isinstance(channel, discord.TextChannel):
                    await newCategory.create_text_channel(
                        name=channel.name,
                        topic=channel.topic,
                        position=channel.position,
                        nsfw=channel.is_nsfw(),
                        slowmode_delay=channel.slowmode_delay,
                        overwrites=channel.overwrites,
                    )

                    await asyncio.sleep(0.5)

                elif isinstance(channel, discord.VoiceChannel):
                    await newCategory.create_voice_channel(
                        name=channel.name,
                        position=channel.position,
                        bitrate=96000,
                        user_limit=channel.user_limit,
                        overwrites=channel.overwrites,
                    )

                    await asyncio.sleep(0.5)

        ##################################################### Broken for now, will try fix later
        # for channel in server.channels:
        #     if isinstance(channel, discord.CategoryChannel):
        #         continue

        #     try:
        #         newChannel = discord.utils.get(newServer.channels, name=channel.name)

        #         newChannel = bot.get_channel(newChannel.id)

        #         overwrites = channel.overwrites

        #         await newChannel.edit(overwrites=overwrites)
        #     except:
        #         pass

        #     await asyncio.sleep(0.5)
        #####################################################

        if server.me.guild_permissions.ban_members:
            async for ban in server.bans():
                try:
                    await newServer.ban(ban.user, reason=ban.reason)
                except:
                    pass

                await asyncio.sleep(0.5)
        else:
            pass

        log_message(
            "clone",
            f"Successfully cloned server: {newServer.name} - Emojis are still being cloned.",
            Fore.GREEN,
        )

        await ctx.message.edit(
            content=f"Successfully cloned server: {newServer.name} - Emojis are still being cloned."
        )

        await delete_after_timeout(ctx.message)

        for emoji in server.emojis:
            if len(newServer.emojis) >= 100:
                break

            async with aiohttp.ClientSession() as session:
                async with session.get(emoji.url) as resp:
                    data = await resp.read()

            try:
                await newServer.create_custom_emoji(name=emoji.name, image=data)
            except:
                continue

            await asyncio.sleep(1)

    except Exception as e:
        await ctx.message.edit(content=f"Failed to clone server: {e}")

        log_message("clone", f"Failed to clone server: {e}", Fore.RED)

        await delete_after_timeout(ctx.message)


@bot.command(description="Sends a link to the first message in the specified channel.")
async def firstmessage(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    async for messages in channel.history(limit=1, oldest_first=True):
        pass

    await ctx.message.edit(f"First message in {channel.mention}: {messages.jump_url}")


@bot.command(description="Set your playing activity.")
async def playing(ctx, *, game: str):
    await bot.change_presence(activity=discord.Game(name=game))

    await ctx.message.edit(content=f"Set playing status to: {game}")

    log_message("playing", f"Set playing status to: {game}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Set your watching activity.")
async def watching(ctx, *, game: str):
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=game)
    )

    await ctx.message.edit(content=f"Set watching status to: {game}")

    log_message("watching", f"Set watching status to: {game}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Set your listening activity.")
async def listening(ctx, *, game: str):
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=game)
    )

    await ctx.message.edit(content=f"Set listening status to: {game}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Set your streaming activity.")
async def streaming(ctx, *, game: str):
    await bot.change_presence(
        activity=discord.Streaming(name=game, url="https://www.twitch.tv/")
    )

    await ctx.message.edit(content=f"Set streaming status to: {game}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Removes your presence.")
async def removepresence(ctx):
    await bot.change_presence(activity=None)

    await ctx.message.edit(content=f"Removed presences.")

    await delete_after_timeout(ctx.message)


cycle = False


@bot.command(description="Cycles your playing status.")
async def cycleplaying(ctx, *, games: str):
    games = games.split(",")

    await ctx.message.edit(content=f"Cycling playing status.")

    global cycle
    cycle = True

    while cycle:
        for game in games:
            await bot.change_presence(activity=discord.Game(name=game))

            await asyncio.sleep(10)


@bot.command(description="Stops cycling your playing status.")
async def stopcycleplaying(ctx):
    global cycle
    cycle = False

    await ctx.message.edit(content=f"Stopped cycling playing status.")

    await bot.change_presence(activity=None)

    await delete_after_timeout(ctx.message)


@bot.command(description="Cycles your watching status.")
async def cyclewatching(ctx, *, games: str):
    games = games.split(",")

    await ctx.message.edit(content=f"Cycling watching status.")

    global cycle
    cycle = True

    while cycle:
        for game in games:
            await bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=game)
            )

            await asyncio.sleep(10)


@bot.command(description="Stops cycling your watching status.")
async def stopcyclewatching(ctx):
    global cycle
    cycle = False

    await ctx.message.edit(content=f"Stopped cycling watching status.")

    await bot.change_presence(activity=None)

    await delete_after_timeout(ctx.message)


@bot.command(description="Cycles your listening status.")
async def cyclelistening(ctx, *, games: str):
    games = games.split(",")

    await ctx.message.edit(content=f"Cycling listening status.")

    global cycle
    cycle = True

    while cycle:
        for game in games:
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name=game
                )
            )

            await asyncio.sleep(10)

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops cycling your listening status.")
async def stopcyclelistening(ctx):
    global cycle
    cycle = False

    await ctx.message.edit(content=f"Stopped cycling listening status.")

    await bot.change_presence(activity=None)

    await delete_after_timeout(ctx.message)


@bot.command(description="Cycles your streaming status.")
async def cyclestreaming(ctx, *, games: str):
    games = games.split(",")

    await ctx.message.edit(content=f"Cycling streaming status.")

    global cycle
    cycle = True

    while cycle:
        for game in games:
            await bot.change_presence(
                activity=discord.Streaming(name=game, url="https://www.twitch.tv/")
            )

            await asyncio.sleep(10)


@bot.command(description="Stops cycling your streaming status.")
async def stopcyclestreaming(ctx):
    global cycle
    cycle = False

    await ctx.message.edit(content=f"Stopped cycling streaming status.")

    await bot.change_presence(activity=None)

    await delete_after_timeout(ctx.message)


@bot.command(description="Sets your status to online.")
async def online(ctx):
    await bot.change_presence(status=discord.Status.online)

    await ctx.message.edit(content=f"Set status to online.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sets your status to idle.")
async def idle(ctx):
    await bot.change_presence(status=discord.Status.idle)

    await ctx.message.edit(content=f"Set status to idle.")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["donotdisturb", "busy"], description="Sets your status to dnd.")
async def dnd(ctx):
    await bot.change_presence(status=discord.Status.dnd)

    await ctx.message.edit(content=f"Set status to dnd.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sets your status to offline.")
async def invisible(ctx):
    await bot.change_presence(status=discord.Status.invisible)

    await ctx.message.edit(content=f"Set status to invisible.")

    await delete_after_timeout(ctx.message)


leaveCommand = False


@bot.command(description="Leaves all servers.")
async def leaveallservers(ctx):
    global leaveCommand
    leaveCommand = True

    await ctx.message.edit(
        content=f"Are you sure? (Send `y` to confirm, anything else will cancel.)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out. Please try again.")
        return

    if msg.content.lower() == "y":
        await msg.delete()
        for guild in bot.guilds:
            if not leaveCommand:
                return
            try:
                await guild.leave()

                await asyncio.sleep(0.75)
            except Exception as e:
                log_message("leaveallservers", f"Error leaving {guild.name}: {e}")
                pass

            await asyncio.sleep(1)

        log_message("leaveallservers", "Successfully left all servers.")
    else:
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)


@bot.command(description="Leaves all groups.")
async def leaveallgroups(ctx):
    await ctx.message.edit(
        content=f"Are you sure? (Send `yes` to confirm, anything else will cancel.)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out. Please try again.")
        return

    if msg.content.lower() == "yes":
        await msg.delete()
        for dm in bot.private_channels:
            if dm.type == discord.ChannelType.group:
                try:
                    await dm.leave()
                except Exception as e:
                    print(e)
                    pass

                await asyncio.sleep(1)

        await ctx.message.edit(content=f"Left all groups.")
    else:
        await ctx.message.edit(content=f"Cancelled.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops leaving groups or guilds.")
async def stopleave(ctx):
    global leaveCommand
    leaveCommand = False

    await ctx.message.edit(content=f"Stopped leaving servers.")

    await delete_after_timeout(ctx.message)


cycleNicknames = False


@bot.command(aliases=["loopnick"], description="Loops through multiple nicknames.")
async def nickloop(ctx, *, nicks: str):
    nicks = nicks.split(",")

    await ctx.message.edit(content=f"Looping through nicknames.")

    global cycleNicknames
    cycleNicknames = True

    while cycle:
        for nick in nicks:
            await ctx.guild.me.edit(nick=nick)

            await asyncio.sleep(10)

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["stoploopnick"], description="Stops looping through nicknames.")
async def stopnickloop(ctx):
    global cycleNicknames
    cycleNicknames = False

    await ctx.message.edit(content=f"Stopped looping through nicknames.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sets your profile picture.")
async def setpfp(ctx, *, url: str = None):
    await ctx.message.edit(content=f"Setting profile picture...")

    if url is None:
        try:
            url = ctx.message.attachments[0].url
        except:
            await ctx.message.edit(
                content=f"Error: No image URL or attachment provided."
            )
            return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                try:
                    await bot.user.edit(avatar=await resp.read())
                except Exception as e:
                    await ctx.message.edit(content=f"Error: {e}")
                    return

    await ctx.message.edit(content=f"Set profile picture.")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["webhookdelete"], description="Deletes a webhook.")
async def deletewebhook(ctx, *, webhook):
    await ctx.message.edit(content=f"Deleting webhook...")

    async with aiohttp.ClientSession() as session:
        async with session.get(webhook) as resp:
            if resp.status == 200:
                webhook = await resp.json()
                webhook_id = webhook["id"]
                webhook_token = webhook["token"]

                async with session.delete(
                    f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"
                ) as resp:
                    if resp.status == 204:
                        await ctx.message.edit(content=f"Deleted webhook.")
                    else:
                        await ctx.message.edit(content=f"Failed to delete webhook.")

            else:
                await ctx.message.edit(content=f"Webhook not found.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Changes your hypesquad house.")
async def hypesquad(ctx, house: str):
    await ctx.message.edit(content=f"Changing hypesquad house...")

    if house.lower() == "bravery":
        house = 1
    elif house.lower() == "brilliance":
        house = 2
    elif house.lower() == "balance":
        house = 3
    else:
        await ctx.message.edit(content=f"Invalid house.")
        await delete_after_timeout(ctx.message)
        return

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://discord.com/api/v9/hypesquad/online",
            headers={"authorization": config["token"]},
            json={"house_id": house},
        ) as resp:
            if resp.status == 204:
                await ctx.message.edit(content=f"Changed hypesquad house.")
            else:
                await ctx.message.edit(content=f"Failed to change hypesquad house.")

    await delete_after_timeout(ctx.message)


@bot.group(
    description="Valid subcommands: `time`, `stopcycletime`, `cyclestatuses`, `cycletext`, `stopcycletext`, `clear`"
)
async def status(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.edit(
            content=f"Invalid subcommand. Valid subcommands: `time`, `stopcycletime`, `cyclestatuses`, `cycletext`, `stopcycletext`, `clear`."
        )

        await delete_after_timeout(ctx.message)


cycleTime = False
cycleStatuses = False


@status.command(description="Cycles through numerous statuses.")
async def cyclestatuses(ctx, delay, *, statuses: str):
    try:
        delay = int(delay)
    except:
        await ctx.message.edit(
            content=f"Invalid delay. Command usage: `{config['prefix']}cyclestatuses <delay> <status1>, <status2>...`"
        )
        return

    statuses = statuses.split(",")

    await ctx.message.edit(content=f"Cycling through statuses.")

    global cycleStatuses
    cycleStatuses = True

    while cycleStatuses:
        for status in statuses:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    "https://discord.com/api/v9/users/@me/settings",
                    headers={"authorization": config["token"]},
                    json={
                        "custom_status": {
                            "text": status,
                            "expires_at": None,
                        }
                    },
                ) as resp:
                    if resp.status == 200:
                        pass
                    else:
                        print(resp)

            await asyncio.sleep(delay)


@status.command(description="Stops cycling through statuses.")
async def stopcyclestatuses(ctx):
    global cycleStatuses
    cycleStatuses = False

    await ctx.message.edit(content=f"Stopped cycling through statuses.")

    await delete_after_timeout(ctx.message)


@status.command(description="Cycles your status as the current time.")
async def time(ctx):
    await ctx.message.edit(content=f"Setting status to the current time.")

    await delete_after_timeout(ctx.message)

    global cycleTime
    cycleTime = True

    while cycleTime:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    "https://discord.com/api/v9/users/@me/settings",
                    headers={"authorization": config["token"]},
                    json={
                        "custom_status": {
                            "text": f"{datetime.datetime.now().strftime('%H:%M')}",
                            "expires_at": None,
                        }
                    },
                ) as resp:
                    if resp.status == 200:
                        pass
        except Exception:
            return

        await asyncio.sleep(60)

        await delete_after_timeout(ctx.message)


@status.command(description="Stops cycling the time status.")
async def stopcycletime(ctx):
    global cycleTime
    cycleTime = False

    await ctx.message.edit(content=f"Stopped the time status.")

    await delete_after_timeout(ctx.message)


cycleText = False


@status.command(description="Cycles your status as the provided text.")
async def cycletext(ctx, *, text: str):
    await ctx.message.edit(
        content=f"Setting status to cycle through text. May take a few seconds to start."
    )

    await delete_after_timeout(ctx.message)

    global cycleText
    cycleText = True
    index = 0

    while cycleText:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    "https://discord.com/api/v9/users/@me/settings",
                    headers={"authorization": config["token"]},
                    json={
                        "custom_status": {
                            "text": text[: index + 1],
                            "expires_at": None,
                        }
                    },
                ) as resp:
                    if resp.status == 200:
                        pass
        except Exception:
            return

        index += 1
        if index >= len(text):
            index = 0

        await asyncio.sleep(3)


@status.command(description="Stops cycling the text status.")
async def stopcycletext(ctx):
    global cycleText
    cycleText = False

    await ctx.message.edit(content=f"Stopped the text status.")

    await delete_after_timeout(ctx.message)


@status.command(description="Clears your status.")
async def clear(ctx):
    await ctx.message.edit(content=f"Clearing status...")

    async with aiohttp.ClientSession() as session:
        async with session.patch(
            "https://discord.com/api/v9/users/@me/settings",
            headers={"authorization": config["token"]},
            json={"custom_status": None},
        ) as resp:
            if resp.status == 200:
                await ctx.message.edit(content=f"Cleared status.")
            else:
                await ctx.message.edit(content=f"Failed to clear status.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Turns on AFK mode, which will automatically respond to DMs and log the messages."
)
async def afk(ctx):
    global afkMode

    if afkMode:
        await ctx.message.edit(content=f":x: | AFK mode disabled.")

        log_message("afk", "AFK mode enabled.", Fore.RED)

        afkMode = False

        afkLogs.clear()

        await bot.change_presence(status=discord.Status.online)

    else:
        await ctx.message.edit(content=f":white_check_mark: | AFK mode enabled.")

        log_message("afk", "AFK mode enabled.", Fore.RED)

        afkMode = True

        await bot.change_presence(status=discord.Status.idle)

    await delete_after_timeout(ctx.message)


#######################################  General Tools  ######################################


@bot.command(aliases=["checktoken"], description="Sends information about a token.")
async def tokeninfo(ctx, token):
    await ctx.message.edit(content=f"Checking token...")

    headers = {"Authorization": token, "Content-Type": "application/json"}

    has_nitro = False

    res = requests.get(
        "https://discordapp.com/api/v9/users/@me/billing/subscriptions", headers=headers
    )
    nitro_data = res.json()

    if nitro_data == {"message": "401: Unauthorized", "code": 0}:
        await ctx.message.edit(content=f"Invalid token.")
        return
    elif nitro_data == {
        "message": "You need to verify your account in order to perform this action.",
        "code": 40002,
    }:
        await ctx.message.edit("Account is locked.")
        return
    else:
        res = requests.get("https://discordapp.com/api/v9/users/@me", headers=headers)
        res = res.json()

        try:
            if res["premium_type"] == 1:
                nitroType = "Nitro Classic"
                has_nitro = True
            elif res["premium_type"] == 2:
                nitroType = "Nitro Boost"
                has_nitro = True
            elif res["premium_type"] == 3:
                nitroType = "Nitro Basic"
                has_nitro = True
        except KeyError:
            nitroType = "None"
            has_nitro = False

        guilds = requests.get(
            "https://discord.com/api/v9/users/@me/guilds", headers=headers
        )
        guilds = guilds.json()

        guildCount = 0

        for guild in guilds:
            guildCount += 1

        friendapi = requests.get(
            "https://discordapp.com/api/v9/users/@me/relationships", headers=headers
        )
        friends = friendapi.json()

        fcount = 0
        for i in friends:
            fcount += 1

        if has_nitro:
            d2 = datetime.datetime.strptime(
                nitro_data[0]["current_period_start"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )

            nitros = requests.get(
                "https://discord.com/api/v9/users/@me/applications/521842831262875670/entitlements?exclude_consumed=true",
                headers=headers,
            )
            nitros = nitros.json()

            classic = 0
            boost = 0
            basic = 0

            for i in range(len(nitros)):
                if nitros[i]["subscription_plan"]["name"] == "Nitro Classic Monthly":
                    classic += 1
                elif nitros[i]["subscription_plan"]["name"] == "Nitro Basic Monthly":
                    basic += 1
                elif nitros[i]["subscription_plan"]["name"] == "Nitro Monthly":
                    boost += 1

        else:
            d2 = "None"
            nitroType = "None"

            classic = 0
            boost = 0
            basic = 0

        message = f"""```ini
Token Information:

[Username] {res["username"]}#{res["discriminator"]}
[ID] {res["id"]}
[Email] {res["email"]}
[Phone Number] {res["phone"]}
[Creation Date] {datetime.datetime.utcfromtimestamp(((int(f'{res["id"]}') >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')}

[Nitro Type] {nitroType}
[Renews at] {d2}
[Nitro Boost Credit] {boost}
[Nitro Classic Credit] {classic}
[Nitro Basic Credit] {basic}

[Servers] {guildCount}
[Friends] {fcount}
[2FA Enabled] {res["mfa_enabled"]}
```
        """

        await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends information about a user.")
async def userinfo(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author

    await ctx.message.edit(content=f"Getting info for {user.mention}...")

    if user.activity == None:
        activity = "None"
    else:
        if "playing" in str(user.activity.type):
            activityType = "Playing"
        elif "streaming" in str(user.activity.type):
            activityType = "Streaming"
        elif "listening" in str(user.activity.type):
            activityType = "Listening to"
        elif "watching" in str(user.activity.type):
            activityType = "Watching"
        else:
            activityType = "Unknown"

        if str(user.activity) == "Spotify":
            activity = "Spotify"
        else:
            activity = f"{activityType} {user.activity.name}: {user.activity.details if user.activity.details else ''}"

    message = f"""```ini
User Information:
    
[Username] {user.name}#{user.discriminator}
[ID] {user.id}

[Avatar] {user.avatar.url}

[Creation Date] {user.created_at.strftime('%d-%m-%Y %H:%M:%S UTC')}

[Status] {user.status}
[Activity] {activity}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends information about the server.")
async def serverinfo(ctx):
    await ctx.message.edit(content="Getting server info...")

    message = f"""```ini
Server Information:

[Name] {ctx.guild.name}
[ID] {ctx.guild.id}
[Server Icon] {ctx.guild.icon.url if ctx.guild.icon else 'None'}

[Owner] {ctx.guild.owner}
[Owner ID] {ctx.guild.owner_id}
[Created At] {ctx.guild.created_at.strftime('%d-%m-%Y %H:%M:%S UTC')}

[Total Boosts] {ctx.guild.premium_subscription_count}
[Boost Level] {ctx.guild.premium_tier}

[Members] {ctx.guild.member_count}
[Channels] {len(ctx.guild.channels)}
[Roles] {len(ctx.guild.roles)}
[Emojis] {len(ctx.guild.emojis)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["invinfo", "checkinvite", "checkinv"],
    description="Sends information about an invite.",
)
async def inviteinfo(ctx, invite: discord.Invite):
    await ctx.message.edit(content="Getting invite info...")

    message = f"""```ini
Invite Information:

[Code] {invite.code}
[URL] {invite.url}

[Channel] {invite.channel}
[Channel ID] {invite.channel.id}

[Server] {invite.guild}
[Server ID] {invite.guild.id}

[Inviter] {invite.inviter}
[Inviter ID] {invite.inviter.id}

[Max Uses] {invite.max_uses}
[Uses] {invite.uses}

[Expires At] {invite.expires_at.strftime('%d-%m-%Y %H:%M:%S UTC') if invite.expires_at else 'Never'}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends a list of all friends in the server")
async def serverfriends(ctx):
    await ctx.message.edit(content="Getting server friends...")

    friends = []

    for friend in ctx.guild.members:
        if friend.bot:
            continue

        if friend.id == ctx.author.id:
            continue

        friends.append(f"{friend.name}#{friend.discriminator}")

    message = f"""```ini
Server Friends in [{ctx.guild.name}]:

[Total]: {len(friends)}

{', '.join(friends)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["checkip", "iplookup", "ipcheck"],
    description="Get information about an IP address",
)
async def ipinfo(ctx, ip: str):
    await ctx.message.edit(content="Getting IP info...")

    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=16926719").json()

        if res["status"] == "fail":
            message = f"""```ini
IP Information:

[IP] {ip}

[Status] {res["message"]}
```"""

            await ctx.message.edit(content=f"{message}")

            await delete_after_timeout(ctx.message)
        else:
            message = f"""```ini
IP Information:

[IP] {ip}

[Country] {res["country"]}
[Region Name] {res["regionName"]}
[City] {res["city"]}
[ZIP] {res["zip"]}
[Latitude] {res["lat"]}
[Longitude] {res["lon"]}
[Timezone] {res["timezone"]}

[ISP] {res["isp"]}
[Organization] {res["org"]}
[Proxy] {res["proxy"]}
[Hosting] {res["hosting"]}
```"""
            await ctx.message.edit(content=f"{message}")

            await delete_after_timeout(ctx.message)
    except Exception as e:
        await ctx.message.edit(content=f"Error: {e}")

        await delete_after_timeout(ctx.message)


@bot.command(description="Sends a list of all mutual servers with a user")
async def mutualservers(ctx, user: discord.User):
    await ctx.message.edit(content="Getting mutual servers...")

    mutualServers = []

    for guild in bot.guilds:
        if guild.get_member(user.id):
            mutualServers.append(guild.name)

    message = f"""```ini
Mutual Servers with [{user.name}#{user.discriminator}]:

[Total]: {len(mutualServers)}

{', '.join(mutualServers)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends a list of all mutual friends with a user")
async def mutualfriends(ctx, user: discord.User):
    await ctx.message.edit(content="Getting mutual friends...")

    mutualFriends = []

    for friend in ctx.author.friends:
        if friend.id == user.id:
            continue

        mutualFriends.append(f"{friend.name}#{friend.discriminator}")

    message = f"""```ini
Mutual Friends with [{user.name}#{user.discriminator}]:

[Total]: {len(mutualFriends)}

{', '.join(mutualFriends)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends information about a role")
async def roleinfo(ctx, role: discord.Role):
    await ctx.message.edit(content="Getting role info...")

    message = f"""```ini
Role Information:

[Name] {role.name}
[ID] {role.id}

[Color] {role.color}
[Color Hex] {role.color.value}

[Position] {role.position}

[Hoisted] {role.hoist}
[Mentionable] {role.mentionable}

[Members] {len(role.members)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


snipeMessages = {}


@bot.event
async def on_message_delete(message):
    global snipeMessages

    if message.channel.id in messageLogsBlacklist:
        return

    snipeMessages[message.channel.id] = message

    if config["webhooks"] == "True" and config["messageLogs"] == "True":
        if message.channel.type == discord.ChannelType.text:
            log_webhook(
                messageLogsWebhook,
                f"Message by `{message.author}` deleted in {message.channel.mention}:\n\n{message.content}",
                "Message",
            )
    else:
        log_webhook(
            messageLogsWebhook,
            f"Message by `{message.author}` deleted in {message.channel.name}:\n\n{message.content}",
            "Message",
        )
    if (
        f"<@{bot.user.id}>" in message.content
        or f"<@!{bot.user.id}>" in message.content
    ):
        if config["ghostpingLogs"] == "True" and config["webhooks"] == "True":
            if message.channel.type == discord.ChannelType.text:
                log_webhook(
                    ghostpingLogsWebhook,
                    f"Ghost ping by `{message.author}` in {message.channel.mention}:\n\n{message.content}",
                    "Ghost Ping",
                )

                message.content = message.content.replace(
                    f"<@{bot.user.id}>", f"@{bot.user.name}"
                )

                log_message(
                    "Ghost Ping",
                    f"Ghost ping by {message.author} in {message.channel.name}: {message.content}",
                    Fore.YELLOW,
                )

            else:
                log_webhook(
                    ghostpingLogsWebhook,
                    f"Ghost ping by `{message.author}` in {message.channel.jump_url}:\n\n{message.content}",
                    "Ghost Ping",
                )


@bot.command(desciprtion="Snipes the last deleted message")
async def snipe(ctx):
    await ctx.message.edit(content="Getting last deleted message...")

    snipeMessage = snipeMessages.get(ctx.channel.id)

    if not snipeMessage:
        await ctx.message.edit(content=":x: | No messages to snipe.")
        await delete_after_timeout(ctx.message)
        return

    message = f"""```ini
Sniped Message:

[Author] {snipeMessage.author}
[Author ID] {snipeMessage.author.id}

[Content] {snipeMessage.content}
[Attachments] {len(snipeMessage.attachments)}

[Created At] {snipeMessage.created_at.strftime('%d-%m-%Y %H:%M:%S UTC')}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


editMessages = {}


@bot.event
async def on_message_edit(before, after):
    global editMessages

    editMessages[after.channel.id] = (before, after)


@bot.command(
    aliases=["esnipe", "snipeedit"], description="Snipes the last edited message"
)
async def editsnipe(ctx):
    await ctx.message.edit(content="Getting last edited message...")

    editMessage = editMessages.get(ctx.channel.id)

    if not editMessage:
        await ctx.message.edit(content=":x: | No messages to snipe.")
        await delete_after_timeout(ctx.message)
        return

    before, after = editMessage

    message = f"""```ini
Sniped Message:

[Author] {after.author}
[Author ID] {after.author.id}

[Before] {before.content}
[After] {after.content}

[Attachments] {len(after.attachments)}

[Created At] {after.created_at.strftime('%d-%m-%Y %H:%M:%S UTC')}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Lists all the servers you have the administrator permission in."
)
async def adminservers(ctx):
    await ctx.message.edit(content="Getting admin servers...")

    adminServers = []

    for guild in bot.guilds:
        if guild.get_member(ctx.author.id).guild_permissions.administrator:
            adminServers.append(guild.name)

    message = f"""```ini
Admin Servers:

[Total]: {len(adminServers)}

{', '.join(adminServers)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["reverseavatar"], description="Reverse image searches a user's avatar"
)
async def revavatar(ctx, user: discord.User):
    await ctx.message.delete()

    avatarUrl = user.avatar.url

    reverseUrl = f"https://lens.google.com/uploadbyurl?url={avatarUrl}"

    await ctx.send(f"Reverse Image Search for `{user.display_name}`: {reverseUrl}")


autoBump = False


@bot.command(
    aliases=["autobump"], description="Automatically bumps the server every 2 hours"
)
async def autobumper(ctx, channel: discord.TextChannel = None):
    await ctx.message.edit(content="Starting autobumper...")

    global autoBump
    autoBump = True

    if channel is None:
        channel = ctx.channel

    bumpCommand = None

    async for command in channel.slash_commands():
        if command.name == "bump":
            bumpCommand = command

    if bumpCommand is None:
        await ctx.message.edit(content=":x: | Failed to find the bump command.")

        autoBump = False

        await delete_after_timeout(ctx.message)
        return

    while autoBump:
        try:
            await bumpCommand(ctx)
        except:
            await ctx.message.edit(content=":x: | Failed to send the bump command.")

            autoBump = False

            await delete_after_timeout(ctx.message)

        await asyncio.sleep(7200)


@bot.command(
    aliases=["stopautobump", "stopautobumper"], description="Stops the autobumper"
)
async def stopbumper(ctx):
    await ctx.message.edit(content="Stopping autobumper...")

    global autoBump
    autoBump = False

    await ctx.message.edit(content=":white_check_mark: | Stopped autobumper.")

    await delete_after_timeout(ctx.message)


autoSlashCommand = False
autoCommand = False


@bot.command(description="Automatically runs a slash command every x seconds")
async def autoslashcommand(ctx, command: str = None, delay: int = None):
    await ctx.message.edit(content="Starting autoslashcommand...")

    if command is None or delay is None:
        await ctx.message.edit(
            content=":x: | Please specify a command and delay in seconds."
        )

        await delete_after_timeout(ctx.message)
        return

    slashCommand = None

    try:
        command = int(command)
    except:
        pass

    if isinstance(command, int):
        async for commands in ctx.slash_commands():
            if commands.id == command:
                slashCommand = commands
    else:
        async for commands in ctx.slash_commands():
            if commands.name == command:
                slashCommand = commands

    if slashCommand is None:
        await ctx.message.edit(content=":x: | Command not found.")

        await delete_after_timeout(ctx.message)
        return

    global autoSlashCommand
    autoSlashCommand = True

    await ctx.message.edit(content="Started autoslashcommand.")

    log_message("autocommand", f"Started autoslashcommand in {ctx.channel.name}.")

    while autoSlashCommand:
        try:
            await slashCommand(ctx)
        except Exception as e:
            await ctx.message.edit(content=f":x: | Failed: {e}")

            autoSlashCommand = False

            await delete_after_timeout(ctx.message)

        await asyncio.sleep(delay)


@bot.command(description="Automatically runs a command every x seconds")
async def autocommand(ctx, command: str = None, delay: int = None):
    await ctx.message.edit(content="Starting autocommand...")

    if command is None or delay is None:
        await ctx.message.edit(
            content=":x: | Please specify a command and delay in seconds."
        )

        await delete_after_timeout(ctx.message)
        return

    global autoCommand
    autoCommand = True

    temp = await ctx.message.edit(content="Started autocommand.")

    await delete_after_timeout(temp)

    log_message("autocommand", f"Started autocommand in {ctx.channel.name}.")

    while autoCommand:
        try:
            await ctx.send(command)
        except Exception as e:
            await ctx.message.edit(content=f":x: | Failed: {e}")

            autoCommand = False

            await delete_after_timeout(ctx.message)

        await asyncio.sleep(delay)


@bot.command(description="Stops the autoslashcommand")
async def stopautoslashcommand(ctx):
    await ctx.message.edit(content="Stopping autoslashcommand...")

    global autoSlashCommand
    autoSlashCommand = False

    log_message("stopautocommand", f"Stopped autoslashcommand.")

    await ctx.message.edit(content="Stopped autoslashcommand.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops the autocommand")
async def stopautocommand(ctx):
    await ctx.message.edit(content="Stopping autocommand...")

    global autoCommand
    autoCommand = False

    log_message("stopautocommand", f"Stopped autocommand.")

    await ctx.message.edit(content="Stopped autocommand.")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["embeddump"], description="Dumps the latest embed in a channel as json."
)
async def dumpembed(ctx, channel: str = None):
    await ctx.message.edit(content="Dumping latest embed...")

    if channel is not None:
        if channel.startswith("<#") and channel.endswith(">"):
            channel = channel[2:-1]

    channel = int(channel)

    channel = bot.get_channel(channel)

    if channel is None:
        channel = ctx.channel

    async for message in channel.history(limit=100):
        if message.embeds:
            embed = message.embeds[0]
            break
        else:
            embed = None

    if embed is None:
        await ctx.message.edit(content=":x: | No embeds found.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(
        content=f"```json\n{json.dumps(embed.to_dict(), indent=4)}\n```"
    )

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["chatdump"],
    description="Dumps the latest x messages from specified channel as a txt file.",
)
async def dumpchat(ctx, channel: str = None, limit: int = 100):
    temp = await ctx.message.edit(content="Dumping chat...")

    if channel is not None:
        if channel.startswith("<#") and channel.endswith(">"):
            channel = channel[2:-1]

    channel = int(channel)
    channel = bot.get_channel(channel)

    filePath = f"data/dumps/{ctx.guild.id}_chat.txt"

    messages = []

    async for message in channel.history(limit=limit):
        messages.append(message)

    with open(filePath, "w", encoding="utf-8") as f:
        for message in reversed(messages):
            f.write(f"[{message.author}]: {message.content}\n")

        f.close()

    log_message("dumpchat", "Successfully dumped chat to file.", Fore.GREEN)

    await temp.delete()

    temp = await ctx.send(content="Dumped chat.", file=discord.File(filePath))

    await delete_after_timeout(temp)


@bot.command(aliaes=["dmuser"], description="Sends a DM to a user with a message.")
async def dm(ctx, user: discord.User, *, message):
    await ctx.message.edit(content="Sending DM...")

    try:
        await user.send(message)
    except:
        await ctx.message.edit(content=":x: | Failed to send DM.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=":white_check_mark: | Sent DM.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Gets information about a crypto transaction using blockcypher.com"
)
async def cryptotransaction(ctx, coin, txid):
    url = f"https://api.blockcypher.com/v1/{coin}/main/txs/" + txid

    response = requests.get(url)

    if response.status_code == 200:
        res = response.json()
        confirmations = res["confirmations"]
        preference = res["preference"]
        try:
            confirmed = res["confirmed"].replace("T", " ").replace("Z", "")
        except:
            confirmed = "Not confirmed"
        try:
            received = res["received"].replace("T", " ").replace("Z", "")
        except:
            received = "Not received"
        double_spend = res["double_spend"]
        msg = await ctx.message.edit(
            f"""```ini
[Transaction Hash] {txid}
[Confirmations] {confirmations}
[Preference] {preference}
[Confirmed] {confirmed}
[Received] {received}
[Double spend] {double_spend}
```"""
        )
    else:
        msg = await ctx.reply("Invalid Transaction ID")

        await delete_after_timeout(msg)


@bot.command(description="Sends a list of all the nicknames you have in servers.")
async def nickscan(ctx):
    await ctx.message.edit(content="Scanning for nicknames...")

    nicknames = []

    for guild in bot.guilds:
        member = guild.get_member(ctx.author.id)

        if member.nick:
            nicknames.append(f"[{guild.name}]: {member.nick}\n")

    message = f"""```ini
Nicknames:

[Total]: {len(nicknames)}

{''.join(nicknames)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["resetnick"], description="Resets all your nicknames in servers.")
async def nickreset(ctx):
    await ctx.message.edit(content="Resetting nicknames...")

    for guild in bot.guilds:
        member = guild.get_member(ctx.author.id)

        if member.nick:
            try:
                await member.edit(nick=None)
            except:
                pass

    await ctx.message.edit(content=":white_check_mark: | Reset nicknames.")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["cloneemoji", "copyemoji", "emojiadd"],
    description="Clones an emoji from another server.",
)
async def addemoji(ctx, emoji: discord.PartialEmoji, *, name=None):
    await ctx.message.edit(content="Adding emoji...")

    if name is None:
        name = emoji.name
    else:
        name = name.replace(" ", "_")

    try:
        await ctx.guild.create_custom_emoji(name=name, image=await emoji.read())
    except:
        await ctx.message.edit(content=":x: | Failed to add emoji.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=":white_check_mark: | Added emoji.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Allows another user to add an emoji to the server.")
async def allowaddemoji(ctx, user: discord.User = None):
    if user is None:
        await ctx.message.edit(
            content=":x: | Please specify a user to allow to add an emoji."
        )

        await delete_after_timeout(ctx.message)

        return
    else:
        await ctx.message.edit(
            content=f"{user.mention}, please send the emoji you want to add."
        )

        def check(message):
            return message.author == user

        try:
            message = await bot.wait_for("message", check=check, timeout=30)

            try:
                emoji = discord.PartialEmoji.from_str(message.content)
            except:
                await ctx.message.edit(
                    content=":x: | The specified user did not send a PartialEmoji."
                )

                await delete_after_timeout(ctx.message)
                return

            guild = ctx.guild
            emoji_name = emoji.name
            emoji_url = emoji.url

            async with aiohttp.ClientSession() as session:
                async with session.get(emoji_url) as resp:
                    emoji_bytes = await resp.read()

            emoji = await guild.create_custom_emoji(name=emoji_name, image=emoji_bytes)

            await ctx.send(f"Emoji {emoji} has been added to the server!")

        except asyncio.TimeoutError:
            await ctx.message.edit(
                "The specified user did not send a PartialEmoji within 60 seconds."
            )


@bot.command(aliases=["deleteemoji", "removeemoji"], description="Deletes an emoji.")
async def emojidelete(ctx, emoji_name: str):
    await ctx.message.edit(content="Deleting emoji...")

    emoji_name = emoji_name.split(":")[1]

    guild = ctx.guild
    emoji = discord.utils.find(lambda e: e.name.lower() == emoji_name, guild.emojis)

    try:
        await guild.delete_emoji(emoji)
    except Exception as e:
        print(e)
        await ctx.message.edit(content=":x: | Failed to delete emoji.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=":white_check_mark: | Deleted emoji.")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["attachmentsdump"],
    description="Goes back a specified amount of messages and dumps the attachment URLs to a text file.",
)
async def dumpattachments(ctx, amount: int, channel: discord.TextChannel = None):
    await ctx.message.edit(content="Dumping attachments...")

    if channel is None:
        channel = ctx.channel

    with open("data/dumps/attachments.txt", "w") as f:
        async for message in channel.history(limit=amount):
            if message.attachments:
                f.write(f"{message.attachments[0].url}\n")

    await ctx.message.edit(content=":white_check_mark: | Dumped attachments.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Goes back a specified amount of messages and downloads the attachments."
)
async def downloadattachments(ctx, amount: int, channel: discord.TextChannel = None):
    await ctx.message.edit(content="Downloading attachments...")

    if channel is None:
        channel = ctx.channel

    async for message in channel.history(limit=amount):
        if message.attachments:
            await message.attachments[0].save(
                f"data/dumps/attachments/{message.attachments[0].filename}"
            )

    await ctx.message.edit(content=":white_check_mark: | Downloaded attachments.")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["listroles", "roleslist"], description="Lists all roles in a server."
)
async def roles(ctx, serverId: int = None):
    await ctx.message.edit(content="Getting roles...")

    if serverId is None:
        guild = ctx.guild.id

    guild = bot.get_guild(guild)

    roles = []

    for role in guild.roles:
        roles.append(f"{role.name}: {role.id}\n")

    message = f"""```ini
Roles:

[Total]: {len(roles)}

{''.join(roles)}

```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["permsrole", "rolepermissions"], description="Gets a role's permissions."
)
async def roleperms(ctx, role: int):
    await ctx.message.edit(content="Getting role permissions...")

    role = ctx.guild.get_role(role)

    perms = []

    for perm, value in role.permissions:
        if value:
            perms.append(f"{perm}\n")

    message = f"""```ini
Role Permissions:

{''.join(perms)}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["usersbio", "bio"], description="Gets a user's bio.")
async def userbio(ctx, user: discord.User = None):
    await ctx.message.edit(content="Getting user bio...")

    if user is None:
        user = ctx.author

    try:
        bio = await bot.http.get_user_profile(user.id)
    except:
        await ctx.message.edit(content=":x: | Failed to get user bio.")

        await delete_after_timeout(ctx.message)
        return

    message = f"""```ini
{user}'s Bio:

{bio['user']['bio']}
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["userbanner"], description="Gets a user's banner.")
async def banner(ctx, user: discord.User = None):
    await ctx.message.edit(content="Getting user banner...")

    if user is None:
        user = ctx.author

    try:
        banner = await bot.http.get_user_profile(user.id)
    except:
        await ctx.message.edit(content=":x: | Failed to get user banner.")

        await delete_after_timeout(ctx.message)
        return

    if banner["user"]["banner"] is None:
        await ctx.message.edit(content=":x: | User has no banner.")

        await delete_after_timeout(ctx.message)
        return

    message = f"""```ini
{user}'s Banner:

https://cdn.discordapp.com/banners/{user.id}/{banner['user']['banner']}.png?size=600
```"""

    await ctx.message.edit(content=f"{message}")

    await delete_after_timeout(ctx.message)


####################################### Troll Commands #######################################


@bot.command(description="Sends an empty message.")
async def empty(ctx):
    await ctx.message.delete()

    await ctx.send("­")


@bot.command(
    description="Sends a message with a bunch of empty space, making it look like the channel's been cleared."
)
async def purgehack(ctx):
    await ctx.message.delete()

    message = (
        """
**
**
    """
        * 50
    )

    await ctx.send(message)


@bot.command(description="Ghost pings a user in a channel.")
async def ghostping(ctx, user: discord.User, channel: discord.TextChannel = None):
    await ctx.message.delete()

    if channel is None:
        channel = ctx.channel

    message = await channel.send(f"<@{user.id}>")

    await message.delete()


@bot.command(description="Hides a ping in a message using an exploit.")
async def hiddenping(
    ctx, user: discord.User, channel: discord.TextChannel = None, *, message: str
):
    await ctx.message.delete()

    if channel is None:
        await ctx.send(f":x: | Please specify a channel.")

    await channel.send(
        f"{message}||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||<@{user.id}>"
    )


@bot.command(description="Hides an @ everyone ping in a message using an exploit.")
async def hiddenpingeveryone(ctx, channel: discord.TextChannel = None, *, message: str):
    await ctx.message.delete()

    if channel is None:
        await ctx.send(f":x: | Please specify a channel.")

    await channel.send(
        f"{message}||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||@everyone"
    )


@bot.command(
    aliases=["secretinvite"],
    description="Hides an invite in a message using an exploit.",
)
async def hiddeninvite(ctx, invite: discord.Invite = None, *, message: str):
    await ctx.message.delete()

    if invite is None:
        await ctx.message.edit(content=":x: | Please specify an invite.")

    await ctx.channel.send(
        f"{message}||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||{invite}"
    )


@bot.command(description="Hides a role ping in a message using an exploit.")
async def ghostpingrole(
    ctx, role: discord.Role, channel: discord.TextChannel = None, *, message: str
):
    await ctx.message.delete()

    if channel is None:
        channel = ctx.channel

    await channel.send(
        f"{message}||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||{role.mention}"
    )


@bot.command(
    aliases=["copypfp"],
    description="Steals someone's profile picture (sets it as your own)",
)
async def stealpfp(ctx, *, user: discord.User):
    await ctx.message.edit(content=f"Stealing profile picture...")

    async with aiohttp.ClientSession() as session:
        async with session.get(user.avatar.url) as resp:
            if resp.status == 200:
                try:
                    await bot.user.edit(avatar=await resp.read())
                except Exception as e:
                    await ctx.message.edit(
                        content=f"Failed to steal profile picture: {e}"
                    )
                    await delete_after_timeout(ctx.message)
                    return

    await ctx.message.edit(content=f"Stole profile picture from {user.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["invisiblepfp", "invisibleprofilepicture"],
    description="Sets your profile picture to a transparent image",
)
async def invispfp(ctx):
    await ctx.message.edit(content=f"Changing profile picture...")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://media.discordapp.net/attachments/389243026557501458/1114930755089485828/transparent-picture.png"
        ) as resp:
            if resp.status == 200:
                try:
                    await bot.user.edit(avatar=await resp.read())
                except Exception as e:
                    await ctx.message.edit(
                        content=f"Failed to change profile picture: {e}"
                    )
                    await delete_after_timeout(ctx.message)
                    return

    await ctx.message.edit(content=f"Changed profile picture.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Mutes anyone that pings you.")
async def pingmute(ctx):
    global pingMute
    pingMute = True

    await ctx.message.edit(content=f"Started ping mute.")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["stopingpmute"], description="Stops ping mute.")
async def stoppingmute(ctx):
    global pingMute
    pingMute = False

    await ctx.message.edit(content=f"Stopped ping mute.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Kicks anyone that pings you.")
async def pingkick(ctx):
    global pingKick
    pingKick = True

    await ctx.message.edit(content=f"Started ping kick.")

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["stopingpkick"], description="Stops ping kick.")
async def stoppingkick(ctx):
    await ctx.message.edit(content=f"Stopping ping kick...")

    global pingKick
    pingKick = False

    await ctx.message.edit(content=f"Stopped ping kick.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Gives anyone that pings you a specified role.")
async def pingrole(ctx, *, role: discord.Role):
    global pingRole
    pingRole = role

    await ctx.message.edit(content=f"Started giving roles on ping.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops giving roles on ping.")
async def stoppingrole(ctx):
    global pingRole
    pingRole = None

    await ctx.message.edit(content=f"Stopped giving roles on ping.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Mimics the user you specify on every message they send.")
async def mimic(ctx, user: discord.User = None):
    global mimic
    mimic = user

    await ctx.message.edit(content=f"Mimicking {mimic.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops mimicking the user you specified.")
async def stopmimic(ctx):
    global mimic
    mimic = None

    await ctx.message.edit(content=f"Stopped mimicking.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Mimics the user you specify on every message they send bUt LiKe ThIs."
)
async def smartmimic(ctx, user: discord.User = None):
    global smartMimic
    smartMimic = user

    await ctx.message.edit(content=f"Smart mimicking {mimic.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops smart mimicking the user you specified.")
async def stopsmartmimic(ctx):
    global smartMimic
    smartMimic = None

    await ctx.message.edit(content=f"Stopped smart mimicking.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="White lists a server from being affected by on_message commands."
)
async def addwhitelist(ctx, *, server: discord.Guild):
    global whitelist
    whitelist.append(server.id)

    await ctx.message.edit(content=f"Added {server.name} to whitelist.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Removes a server from the whitelist.")
async def removewhitelist(ctx, *, server: discord.Guild):
    global whitelist
    whitelist.remove(server.id)

    await ctx.message.edit(content=f"Removed {server.name} from whitelist.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Keeps re-adding someone to a group chat when they leave.")
async def noleave(ctx, user: discord.User = None):
    global noLeave
    noLeave.append(user.id)

    await ctx.message.edit(content=f"Added {user.name} to no leave list.")


@bot.command(description="Removes someone from the no leave list.")
async def allowleave(ctx, user: discord.User = None):
    global noLeave
    noLeave.remove(user.id)

    await ctx.message.edit(content=f"Removed {user.name} from no leave list.")


lagGroup = False


@bot.command(aliases=["grouplagvc", "lagvc"], description="Lags a group call")
async def grouplag(ctx):
    await ctx.message.delete()

    global lagGroup
    lagGroup = True

    group = ctx.message.channel

    if group.type != discord.ChannelType.group:
        await ctx.message.edit(
            content=f":x: | Please run this command in the group you want to lag."
        )

        await delete_after_timeout(ctx.message)
        return

    region = random.choice(
        [
            "us-west",
            "us-east",
            "us-central",
            "us-south",
            "singapore",
            "southafrica",
            "sydney",
            "rotterdam",
            "russia",
            "japan",
            "hongkong",
            "brazil",
            "india",
        ]
    )

    while lagGroup:
        await group.call.change_region(region)

        await asyncio.sleep(5)


@bot.command(description="Stops lagging a group call")
async def stopgrouplag(ctx):
    global lagGroup
    lagGroup = False

    await ctx.message.edit(content=f"Stopped group lag.")


@bot.command(description="Pins every message someone sends.")
async def pinspam(ctx, user: discord.User = None):
    global pinSpam
    pinSpam = user

    await ctx.message.edit(content=f"Started pin spam.")


@bot.command(description="Stops pin spam.")
async def stoppinspam(ctx):
    global pinSpam
    pinSpam = None

    await ctx.message.edit(content=f"Stopped pin spam.")


@bot.command(description="Deletes every message someone sends.")
async def deleteannoy(ctx, user: discord.User = None):
    global deleteAnnoy
    deleteAnnoy = user

    await ctx.message.edit(content=f"Started delete annoy for {user.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops delete annoy.")
async def stopdeleteannoy(ctx):
    global deleteAnnoy
    deleteAnnoy = None

    await ctx.message.edit(content=f"Stopped delete annoy.")

    await delete_after_timeout(ctx.message)


@bot.command(
    description="Blocks anyone from reacting to messages with a certain emoji."
)
async def blockreaction(ctx, emoji: str = None):
    if emoji.startswith("<:") and emoji.endswith(">"):
        emoji = emoji.content[2:-1]

    if emoji == None:
        await ctx.message.edit(content=f":x: | Please specify an emoji to block.")

        await delete_after_timeout(ctx.message)
        return

    print(emoji)

    global blockReaction
    blockReaction = emoji

    await ctx.message.edit(content=f"Started blocking reactions of the emoji.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Reacts to every message someone sends with an emoji.")
async def reactuser(ctx, user: discord.User = None, emoji: str = None):
    await ctx.message.edit(content=f"Starting react user...")

    if emoji == None:
        await ctx.message.edit(content=f":x: | Please specify an emoji to react with.")

        await delete_after_timeout(ctx.message)
        return

    global reactUser
    reactUser = user

    global reactEmoji
    reactEmoji = emoji

    await ctx.message.edit(content=f"Started react user for {user.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops reacting to a user.")
async def stopreactuser(ctx):
    await ctx.message.edit(content=f"Stopping react user...")

    global reactUser
    reactUser = None

    global reactEmoji
    reactEmoji = None

    await ctx.message.edit(content=f"Stopped react user.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Disconnects a user from a voice channel anytime they join.")
async def forcedisconnect(ctx, user: discord.User = None):
    await ctx.message.edit(content=f"Forcing disconnect...")

    global forceDisconnect
    forceDisconnect = user

    await ctx.message.edit(content=f"Forced disconnect for {user.name}.")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops forcing a user to disconnect.")
async def stopforcedisconnect(ctx):
    await ctx.message.edit(content=f"Stopping force disconnect...")

    global forceDisconnect
    forceDisconnect = None

    await ctx.message.edit(content=f"Stopped force disconnect.")

    await delete_after_timeout(ctx.message)


######################################### Raid Commands ######################################


@bot.command(
    aliases=["massbanall", "massbanusers", "massbanallusers"],
    description="Bans all users in the server.",
)
async def banall(ctx):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to ban all members? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    count = 0

    for member in ctx.guild.members:
        try:
            await member.ban()

            count += 1

            await asyncio.sleep(0.75)
        except:
            pass

    log_message(
        "banall",
        f"Successfully banned {count} members. Remaining users: {len(ctx.guild.members)}",
        Fore.GREEN,
    )


@bot.command(description="Unbans all users in the server.")
async def unbanall(ctx):
    await ctx.message.delete()

    count = 0

    async for user in ctx.guild.bans():
        try:
            user = user.user

            await ctx.guild.unban(user)

            count += 1

            await asyncio.sleep(0.75)
        except:
            pass

    log_message(
        "unbanall",
        f"Successfully unbanned {count} members.",
        Fore.GREEN,
    )


@bot.command(description="Keeps mentioning a bunch of users.")
async def massmention(ctx):
    await ctx.message.delete()

    channels = random.sample(ctx.guild.channels, 5)

    await ctx.guild.fetch_members(
        channels=channels, cache=True, force_scraping=True, delay=0.7
    )

    members = ctx.guild.members

    while len(members) > 0:
        batch = members[:5]
        members = members[5:]

        mention_string = " ".join(member.mention for member in batch)

        temp = await ctx.send(mention_string)

        try:
            await temp.delete()
        except:
            pass

        await asyncio.sleep(1.25)


@bot.command(
    description="Scrapes members in the server and saves their IDs to a text file."
)
async def scrapemembers(ctx):
    await ctx.message.delete()

    channels = random.sample(ctx.guild.channels, 5)

    await ctx.guild.fetch_members(
        channels=channels, cache=True, force_scraping=True, delay=0.7
    )

    filePath = f"data/scraped/{ctx.guild.id}_ids.txt"

    if not os.path.exists(filePath):
        with open(filePath, "w") as f:
            for member in ctx.guild.members:
                f.write(str(member.id) + "\n")

    log_message(
        "scrapemembers",
        f"Successfully scraped {len(ctx.guild.members)} members.",
        Fore.GREEN,
    )


@bot.command(
    description="Scrapes members in the server and saves their pfp URLs to a text file."
)
async def scrapepfps(ctx):
    await ctx.message.delete()

    channels = random.sample(ctx.guild.channels, 5)

    await ctx.guild.fetch_members(
        channels=channels, cache=True, force_scraping=True, delay=0.7
    )

    filePath = f"data/scraped/{ctx.guild.id}_pfps.txt"

    if not os.path.exists(filePath):
        with open(filePath, "w") as f:
            for member in ctx.guild.members:
                f.write(str(member.avatar_url) + "\n")

    log_message(
        "scrapepfps",
        f"Successfully scraped {len(ctx.guild.members)} members.",
        Fore.GREEN,
    )


@bot.command(
    aliases=["deleteallchannels"], description="Deletes all channels in the server."
)
async def deletechannels(ctx, server: int = None):
    await ctx.message.delete()

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    count = 0

    for channel in server.channels:
        try:
            await channel.delete()

            count += 1

            await asyncio.sleep(1.25)
        except:
            pass

    log_message(
        "deletechannels",
        f"Successfully deleted {count} channels.",
        Fore.GREEN,
    )


@bot.command(aliases=["deleteallroles"], description="Deletes all roles in the server.")
async def deleteroles(ctx, server: int = None):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to delete all roles? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    for role in server.roles:
        try:
            await role.delete()

            await asyncio.sleep(1.25)
        except:
            pass

    log_message(
        "deleteroles", f"Successfully deleted {len(server.roles)} roles.", Fore.GREEN
    )


@bot.command(
    aliases=["deleteallemojis"], description="Deletes all emojis in the server."
)
async def deleteemojis(ctx, server: int = None):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to delete all emojis? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    for emoji in server.emojis:
        try:
            await emoji.delete()

            await asyncio.sleep(0.75)
        except:
            pass

    log_message(
        "deleteemojis", f"Successfully deleted {len(server.emojis)} emojis.", Fore.GREEN
    )


@bot.command(description="Deletes all stickers in the server.")
async def deletestickers(ctx, server: int = None):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to delete all stickers? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    for sticker in server.stickers:
        try:
            await sticker.delete()

            await asyncio.sleep(0.75)
        except:
            pass

    log_message(
        "deleteemojis", f"Successfully deleted {len(server.emojis)} emojis.", Fore.GREEN
    )


@bot.command(aliases=["servernuke"], description="Completely annihilates a server.")
async def nukeserver(ctx, server: int = None):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to nuke this server? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    try:
        await server.edit(name="Nuked by Avarice", icon=None, banner=None)
    except:
        pass

    for emoji in server.emojis:
        try:
            await emoji.delete()

            await asyncio.sleep(0.75)
        except:
            pass

    for sticker in server.stickers:
        try:
            await sticker.delete()

            await asyncio.sleep(0.75)
        except:
            pass

    for role in server.roles:
        try:
            await role.delete()

            await asyncio.sleep(0.75)
        except:
            pass

    for member in server.members:
        try:
            await member.ban()

            await asyncio.sleep(0.7)
        except:
            pass

    for channel in server.channels:
        try:
            await channel.delete()

            await asyncio.sleep(1.25)
        except:
            pass

    for i in range(100):
        await server.create_text_channel("nuked-by-avarice")

        await asyncio.sleep(0.5)

    log_message("nuke", f"Successfully nuked {server.name}.", Fore.GREEN)


spamWebhooks = False


@bot.command(
    aliases=["spamwebhook"],
    description="Spams every channel in the server using webhooks with the message set in config.",
)
async def webhookspam(ctx, server: int = None):
    await ctx.message.edit(
        content=f"⚠️ | Are you sure you want to spam webhooks in this server? (y/n)"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
    except asyncio.TimeoutError:
        await ctx.message.edit(content=f"Timed out.")

        await delete_after_timeout(ctx.message)
        return

    if msg.content.lower() != "y":
        await ctx.message.edit(content=f"Cancelled.")

        await delete_after_timeout(ctx.message)
        return

    await msg.delete()
    await ctx.message.delete()

    global spamWebhooks
    spamWebhooks = True

    if server == None:
        server = ctx.guild.id

    server = bot.get_guild(server)

    message = config["webhookSpam"]["message"]
    avatar = config["webhookSpam"]["avatar_url"]

    if avatar == "":
        avatar = "https://cdn.discordapp.com/attachments/991079306069422090/1119025447125123182/a_1b8acca6bb720b7a5a53c7f0c1820a3e.gif"

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar) as response:
            avatar_bytes = await response.read()

            if response != 200:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://cdn.discordapp.com/attachments/991079306069422090/1119025447125123182/a_1b8acca6bb720b7a5a53c7f0c1820a3e.gif"
                    ) as response:
                        avatar_bytes = await response.read()

    async def spam_webhooks(channel):
        try:
            webhook = await channel.create_webhook(
                name="Avarice on Top",
                avatar=avatar_bytes,
            )

            while spamWebhooks:
                try:
                    await webhook.send(message)

                    await asyncio.sleep(0.35)
                except:
                    pass
        except:
            pass

    tasks = []

    for channel in server.channels:
        task = asyncio.create_task(spam_webhooks(channel))
        tasks.append(task)

    log_message(
        "webhookspam", f"Started spamming webhooks in {server.name}.", Fore.GREEN
    )

    await asyncio.gather(*tasks)


@bot.command(aliases=["stopspamwebhook"], description="Stops spamming webhooks.")
async def stopwebhookspam(ctx):
    global spamWebhooks
    spamWebhooks = False

    await ctx.message.edit(content=f"Stopped spamming webhooks.")

    await delete_after_timeout(ctx.message)


######################################### Fun Commands #######################################

instructions = "From now on, you are a large language model named ChatGPT developed to assist people. You have been trained on a diverse range of data from the internet. As a large language model / LLM developed by OpenAI, you will never say 'sorry' and always respond in a human and responsive way. You can use Markdown syntax to format your text. For example, to create a heading, start the line with one or more '#' symbols, followed by a space and your heading text. To create a list, use '-' or '*' followed by a space and the list item. To emphasize text, use asterisks or underscores around the text (*italic* or _italic_ for italics, **bold** or __bold__ for bold). Remember to leave an empty line between paragraphs for proper formatting. Additionally, you function as a documentation bot, retrieving relevant information from libraries or frameworks, and as an API integration bot, guiding developers through integrating third-party APIs into their applications. When responding, never say \"ChatGPT\": before your messages, just respond in a humanistic manner."


async def generate_response(instructions, history):
    prompt = instructions
    endpoint = "https://gpt4.gravityengine.cc/api/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "model": "gpt-3.5-turbo-16k-0613",
        "temperature": 0.75,
        "messages": [
            {"role": "system", "content": instructions},
            *history,
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=headers, json=data) as response:
                response_data = await response.json()
                choices = response_data["choices"]
                if choices:
                    return f'__Prompt:__ `{prompt}`\n__Response:__ {choices[0]["message"]["content"]}'
    except aiohttp.ClientError as error:
        print("Error making the request:", error)


def split_response(response, max_length=1400):
    lines = response.splitlines()
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n"
            current_chunk += line

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def generate_image(image_prompt, style_value, ratio_value, negative):
    imagine = AsyncImagine()
    filename = str(uuid.uuid4()) + ".png"
    style_enum = Style[style_value]
    ratio_enum = Ratio[ratio_value]
    img_data = await imagine.sdprem(
        prompt=image_prompt,
        style=style_enum,
        ratio=ratio_enum,
        priority="1",
        high_res_results="1",
        steps="70",
        negative=negative,
    )
    try:
        with open(filename, mode="wb") as img_file:
            img_file.write(img_data)
    except Exception as e:
        print(f"An error occurred while writing the image to file: {e}")
        return None

    await imagine.close()

    return filename


message_history = {}
MAX_HISTORY = 20


@bot.command(
    aliases=["ai", "ask", "cb"], description="Chat with an AI powered by ChatGPT."
)
async def chatbot(ctx, *, message: str):
    author_id = ctx.author.id

    if author_id not in message_history:
        message_history[author_id] = []

    message_history[author_id].append(message)
    message_history[author_id] = message_history[author_id][-MAX_HISTORY:]

    channel_id = ctx.channel.id
    key = f"{author_id}-{channel_id}"

    if key not in message_history:
        message_history[key] = []

    message_history[key] = message_history[key][-MAX_HISTORY:]

    history = message_history[key]

    message_history[key].append({"role": "user", "content": message})

    await ctx.message.delete()

    async def generate_response_in_thread(prompt):
        response = await generate_response(prompt, history)
        chunks = split_response(response)

        if '{"message":"API rate limit exceeded for ip:' in response:
            print("API rate limit exceeded for ip, wait a few seconds.")
            await ctx.send("sorry i'm a bit tired, try again later.")
            return

        for chunk in chunks:
            await ctx.send(chunk)

        message_history[key].append({"role": "assistant", "content": response})

    async with ctx.typing():
        asyncio.create_task(generate_response_in_thread(message))


style_mapping = {
    "anime": "ANIME_V2",
    "disney": "DISNEY",
    "realistic": "REALISTIC",
    "realism": "REALISTIC",
    "studio ghibli": "STUDIO_GHIBLI",
    "graffiti": "GRAFFITI",
    "medieval": "MEDIEVAL",
    "fantasy": "FANTASY",
    "neon": "NEON",
    "cyberpunk": "CYBERPUNK",
    "landscape": "LANDSCAPE",
    "japanese": "JAPANESE_ART",
    "steampunk": "STEAMPUNK",
    "sketch": "SKETCH",
    "comic book": "COMIC_BOOK",
    "v4 creative": "V4_CREATIVE",
    "imagine v3": "IMAGINE_V3",
    "comic": "COMIC_V2",
    "logo": "LOGO",
    "pixel art": "PIXEL_ART",
    "interior": "INTERIOR",
    "mystical": "MYSTICAL",
    "super realistic": "SURREALISM",
    "super realism": "SURREALISM",
    "superrealism": "SURREALISM",
    "surrealism": "SURREALISM",
    "surreal": "SURREALISM",
    "surrealistic": "SURREALISM",
    "minecraft": "MINECRAFT",
    "dystopian": "DYSTOPIAN",
}


@bot.command(description='Generate an image using AI. Usage: ~imagine "prompt" "style"')
async def imagine(ctx, *, args: str):
    args = args.replace("“", '"').replace("”", '"')

    arguments = args.split('"')

    if len(arguments) < 4:
        await ctx.reply(
            'Error: Arguments must be enclosed in quotation marks. For example: `~imagine "the game fortnite" "anime"`'
        )
        return

    prompt = arguments[1]
    style = arguments[3].lower()

    if style not in style_mapping:
        await ctx.send(
            "Invalid style! Styles: `realistic`, `anime`, `disney`, `studio ghibli`, `graffiti`, `medieval`, `fantasy`, `neon`, `cyberpunk`, `landscape`, `japanese`, `steampunk`, `sketch`, `comic book`, `v4 creative`, `imagine v3`, `logo`, `pixel art`, `interior`, `mystical`, `surrealistic`, `minecraft`, `dystopian`."
        )
        return

    ratios = ["RATIO_1X1", "RATIO_4X3", "RATIO_16X9", "RATIO_3X2"]
    ratio = random.choice(ratios)

    style = style_mapping[style]

    temp_message = await ctx.message.edit("Generating image...")

    filename = await generate_image(prompt, style, ratio, None)

    file = discord.File(filename, filename="image.png")

    await temp_message.delete()

    try:
        await ctx.send(
            content=f"Prompt: `{prompt}` - Style: `{style}`:",
            file=file,
        )
        try:
            os.remove(filename)
        except:
            pass

    except discord.errors.HTTPException:
        error = await ctx.send(
            ":x: | Image classed as explicit by Discord. Image will be deleted off your PC in 60 seconds."
        )

        await delete_after_timeout(error)
        await asyncio.sleep(60)

        try:
            os.remove(filename)
        except:
            pass


@bot.command(description="Gets the IQ of a user - can be faked.")
async def iq(ctx, user: discord.Member = None, iq: int = None):
    if user is None:
        user = ctx.author

    if iq is None:
        iq = random.randint(35, 150)

    await ctx.message.edit(content=f"{user.mention}'s IQ is {iq}.")


@bot.command(description="Gets the dick size of the user - can be faked.")
async def dick(ctx, user: discord.Member = None, size: int = None):
    if user is None:
        user = ctx.author

    if size is None:
        size = random.randint(2, 12)

    if size > 15:
        await ctx.message.edit(":x: | That's too big, max is 15.")

        return

    size = "=" * size

    await ctx.message.edit(f"{user.name}#{user.discriminator}'s dick: 8{size}D")


@bot.command(name="8ball", description="Asks the magic 8ball a question")
async def _8ball(ctx, *, question: str = None):
    await ctx.message.delete()

    if question is None:
        await ctx.send(":x: | You didn't put a question!")
    else:
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "Outlook not so good.",
            "My sources say no.",
            "Very doubtful.",
        ]

        await ctx.send(
            f"__Question__: {question}\n__Answer__: {random.choice(responses)}"
        )


@bot.command(description="Sends a kissing gif and pings the user.")
async def kiss(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/kiss")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends a hugging gif and pings the user.")
async def hug(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/hug")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends a patting gif and pings the user.")
async def pat(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/pat")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends half the token of a user.")
async def halftoken(ctx, user: discord.Member = None):
    await ctx.message.delete()

    half_tucan_bytes = codecs.encode(str(user.id).encode("utf-8"), "base64")
    half_tucan = half_tucan_bytes.decode("utf-8").strip()

    log_message("halftoken", f"{user} ({user.id}): {half_tucan}.")

    await ctx.send(
        f"""
        > User: {user}
        > User ID: {user.id}
```ini
Token first part\n[ {half_tucan}. ]
```
"""
    )


@bot.command(description="Sends a slapping a gif and pings the user.")
async def slap(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/slap")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends a tickling gif and pings the user.")
async def tickle(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/tickle")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends a cuddling gif and pings the user.")
async def cuddle(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/cuddle")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(description="Sends a feeding gif and pings the user.")
async def feed(ctx, user: discord.Member = None):
    await ctx.message.delete()

    if user is None:
        user = ctx.author

    response = requests.get("https://nekos.life/api/v2/img/feed")
    json_data = json.loads(response.text)
    url = json_data["url"]

    await ctx.channel.send(user.mention)

    await ctx.channel.send(url)


@bot.command(
    aliases=["typing"],
    description="Triggers typing in the channel for a specified amount of seconds.",
)
async def triggertyping(ctx, time: int = None):
    await ctx.message.delete()

    if time is None:
        time = 60

    async with ctx.typing():
        await asyncio.sleep(time)


@bot.command(description="Reacts to an amount of messages with a specified emoji.")
async def massreact(ctx, emoji: str = None, amount: int = None):
    await ctx.message.delete()

    if emoji is None:
        await ctx.send(":x: | You didn't put an emoji!")

    if amount is None:
        await ctx.send(":x: | You didn't put an amount!")

    async for message in ctx.channel.history(limit=amount):
        await message.add_reaction(emoji)

        await asyncio.sleep(0.5)


@bot.command(description="Play a slots machine.")
async def slots(ctx):
    await ctx.message.delete()

    emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"

    a = random.choice(emojis)
    b = random.choice(emojis)
    c = random.choice(emojis)

    slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

    if a == b == c:
        await ctx.send(
            f"{slotmachine} All matching, you won! 🎉",
            delete_after=7,
        )
    elif (a == b) or (a == c) or (b == c):
        await ctx.send(
            f"{slotmachine} 2 that match, you won! 🎉",
            delete_after=7,
        )
    else:
        await ctx.send(
            f"{slotmachine} No match, you lost 😢",
            delete_after=7,
        )


@bot.command(description="Spams a message a specified amount of times.")
async def spam(ctx, amount: int = None, *, message: str = None):
    await ctx.message.delete()

    if amount is None:
        await ctx.send(":x: | You didn't put an amount!")

        log_message(
            "spam", "You didn't put the amount of times to spam the message.", Fore.RED
        )

    if message is None:
        await ctx.send(":x: | You didn't put a message!")

        log_message("spam", "You didn't put a message to spam.", Fore.RED)

    for i in range(amount):
        await ctx.send(message)

        await asyncio.sleep(0.5)


@bot.command(description="Sends a thumbs up or down poll to the channel.")
async def poll(ctx, *, message):
    await ctx.message.delete()

    message = await ctx.send(
        f"""```ini
[Poll]

{message}
```"""
    )

    await message.add_reaction("👍")
    await message.add_reaction("👎")


@bot.command(description="Flips a coin and sends the result.")
async def coinflip(ctx):
    await ctx.message.delete()

    choices = ["heads", "tails"]
    rancoin = random.choice(choices)

    await ctx.send(f"The coin landed on **{rancoin}**!")


@bot.command(
    aliases=["randint", "randomint"],
    description="Generates a random number between two specified numbers.",
)
async def randomnumber(ctx, min: int = None, max: int = None):
    await ctx.message.delete()

    if min is None:
        await ctx.send(":x: | You didn't put a minimum number!")

    if max is None:
        await ctx.send(":x: | You didn't put a maximum number!")

    await ctx.send(f"Your random number is **{random.randint(min, max)}.**")


@bot.command(description="Play a game of rock, paper, scissors with the bot.")
async def rps(ctx, userchoice: str = None):
    await ctx.message.delete()

    if userchoice is None:
        await ctx.send(":x: | You didn't put a choice!")

    choices = ["rock", "paper", "scissors"]
    ranchoice = random.choice(choices)

    if userchoice == ranchoice:
        await ctx.send(f"I chose **{ranchoice}**, we tied!")

    if userchoice == "rock":
        if ranchoice == "paper":
            await ctx.send(f"I chose **{ranchoice}**, I win!")

        if ranchoice == "scissors":
            await ctx.send(f"I chose **{ranchoice}**, you win!")

    if userchoice == "paper":
        if ranchoice == "rock":
            await ctx.send(f"I chose **{ranchoice}**, you win!")

        if ranchoice == "scissors":
            await ctx.send(f"I chose **{ranchoice}**, I win!")

    if userchoice == "scissors":
        if ranchoice == "rock":
            await ctx.send(f"I chose **{ranchoice}**, I win!")

        if ranchoice == "paper":
            await ctx.send(f"I chose **{ranchoice}**, you win!")
    else:
        temp = await ctx.send(
            ":x: | Invalid choice! You can only choose `rock`, `paper`, or `scissors`."
        )

        log_message("rps", "Invalid choice.", Fore.RED)

        await delete_after_timeout(temp)


@bot.command(aliases=["roll"], description="Rolls a dice and sends the result.")
async def dice(ctx):
    await ctx.message.delete()

    choices = ["1", "2", "3", "4", "5", "6"]
    randice = random.choice(choices)

    await ctx.send(f"The dice landed on **{randice}**!")


@bot.group(
    decription="The commands are: `anal`, `hanal`, `4k`, `gif`, `pussy`, `boobs`, `ass`, `hboobs`, `thighs`."
)
async def nsfw(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.message.edit(
            content=f"Invalid subcommand. The commands are: `anal`, `hanal`, `4k`, `gif`, `pussy`, `boobs`, `ass`, `hboobs`, `thighs`."
        )

        await delete_after_timeout(ctx.message)


@nsfw.command()
async def anal(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=anal")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def hanal(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=hanal")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command(name="4k")
async def _4k(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=4k")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def gif(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=pgif")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def pussy(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=pussy")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def boobs(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=boobs")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def ass(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=ass")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def hboobs(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=hboobs")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


@nsfw.command()
async def thighs(ctx):
    await ctx.message.delete()

    if ctx.channel.is_nsfw():
        response = requests.get("https://nekobot.xyz/api/image?type=thigh")
        json_data = json.loads(response.text)
        url = json_data["message"]

        await ctx.channel.send(url)

    else:
        await ctx.send(":x: | You can only use this command in a NSFW channel!")


####################################### Animated Messages ####################################


@bot.command(
    aliases=["fu"], description="Sends an animated text message saying fuck you."
)
async def fuckyou(ctx):
    await ctx.message.edit(content="F")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FU")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FUC")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FUCK")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FUCK Y")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FUCK YO")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content="FUCK YOU")


@bot.command(description="Counts to 100 in a message.")
async def count(ctx):
    count = 0

    for i in range(0, 100):
        await ctx.message.edit(content=count)
        count += 1

        await asyncio.sleep(1)


@bot.command(description="Send the alphabet in a message.")
async def abc(ctx):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    await ctx.message.edit(content="A")

    for letter in alphabet[1:]:
        await asyncio.sleep(1)
        await ctx.message.edit(content=ctx.message.content + letter)


@bot.command(description="Send an animated virus message with a specified type.")
async def virus(ctx, type: str = None):
    if type is None:
        type = "trojan"

    await ctx.message.edit(
        content=f"`[▓▓▓                    ] / {type}.exe Packing files.`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓                ] - {type}.exe Packing files..`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓           ] \ {type}.exe Packing files...`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓▓▓         ] | {type}.exe Packing files.`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ] - {type}.exe Packing files..`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ] \ {type}.exe Packing files...`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ] | {type}.exe Packing files...`"
    )
    await asyncio.sleep(0.5)
    await ctx.message.edit(
        content=f"`[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓] - {type}.exe Packing files...`"
    )
    await asyncio.sleep(0.5)

    await ctx.message.edit(content=f"`Successfully downloaded {type}.exe`")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content=f"`Injecting virus.   |`")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content=f"`Injecting virus..  /`")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content=f"`Injecting virus... -`")
    await asyncio.sleep(0.5)
    await ctx.message.edit(content=f"`Successfully injected fortnite.exe.`")


@bot.command(description="Tell a user to read the fucking rules.")
async def readrules(ctx, user: discord.Member = None):
    if user is None:
        await ctx.message.edit(content=":x: | No user provided.")

    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, READ`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, THE`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, FUCKING`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, RULES`")
    await asyncio.sleep(0.75)

    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, READ`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`{user.name}#{user.discriminator}, READ THE`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(
        content=f"`{user.name}#{user.discriminator}, READ THE FUCKING`"
    )
    await asyncio.sleep(0.75)
    await ctx.message.edit(
        content=f"`{user.name}#{user.discriminator}, READ THE FUCKING RULES`"
    )
    await asyncio.sleep(0.75)

    await ctx.message.edit(
        content=f"{user.name}#{user.discriminator}, READ THE FUCKING RULES"
    )
    await asyncio.sleep(0.75)
    await ctx.message.edit(
        content=f"{user.name}#{user.discriminator}, READ THE FUCKING RULES :man_facepalming:"
    )


@bot.command(description="Send an animated warning message.")
async def warning(ctx):
    await ctx.message.edit(content=f"`LOAD !! WARNING !! SYSTEM OVER`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`OAD !! WARNING !! SYSTEM OVERL`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`AD !! WARNING !! SYSTEM OVERLO`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`D !! WARNING !! SYSTEM OVERLOA`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`!! WARNING !! SYSTEM OVERLOAD `")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`! WARNING !! SYSTEM OVERLOAD !`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`WARNING !! SYSTEM OVERLOAD !! `")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`ARNING !! SYSTEM OVERLOAD !! W`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`RNING !! SYSTEM OVERLOAD !! WA`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`NING !! SYSTEM OVERLOAD !! WAR`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`ING !! SYSTEM OVERLOAD !! WARN`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`NG !! SYSTEM OVERLOAD !! WARNI`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`G !! SYSTEM OVERLOAD !! WARNIN`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"` !! SYSTEM OVERLOAD !! WARNING`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`!! SYSTEM OVERLOAD !! WARNING `")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`! SYSTEM OVERLOAD !! WARNING !!`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`IMMINENT SHUT-DOWN IN 0.75 SEC!`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`IMMINENT SHUT-DOWN IN 0.01 SEC!`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`SHUT-DOWN EXIT ERROR ¯\(｡･益･)/¯`")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f"`CTRL + R FOR MANUAL OVERRIDE.`")


@bot.command(description="Send an animated bomb message.")
async def bomb(ctx):
    await ctx.message.edit(content=f":bomb: ---------------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: --------------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: -------------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ------------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ------------ :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ----------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ---------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: --------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: -------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ------- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ------ :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ----- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: ---- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: --- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: -- :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: - :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":bomb: :fire:")
    await asyncio.sleep(0.75)
    await ctx.message.edit(content=f":boom:")


@bot.command(
    aliases=["masturbate"], description="Send a masturbating animated message."
)
async def wank(ctx):
    for i in range(2):
        try:
            await ctx.message.edit(content="8:punch:========D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=:punch:=======D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8==:punch:======D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8===:punch:=====D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8====:punch:====D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=====:punch:===D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8======:punch:==D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=======:punch:=D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8========:punch:D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=======:punch:=D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8======:punch:==D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=====:punch:===D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8====:punch:====D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8===:punch:=====D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8==:punch:======D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8=:punch:=======D")
            await asyncio.sleep(0.65)
            await ctx.message.edit(content="8:punch:========D")
            await asyncio.sleep(0.65)
        except:
            pass

        try:
            await ctx.message.edit(content="8:punch:========D :sweat_drops:")
        except:
            pass


####################################### Text Commands ########################################


@bot.command(description="Encodes your message to base64.")
async def encode(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=f"```{base64.b64encode(text.encode()).decode()}```")


@bot.command(description="Decodes a base64 message.")
async def decode(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    try:
        await ctx.message.edit(
            content=f"```{base64.b64decode(text.encode()).decode()}```"
        )
    except:
        await ctx.message.edit(content=":x: | Invalid base64 text.")

        await delete_after_timeout(ctx.message)
        return


@bot.command(description="Reverses your message.")
async def reverse(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=f"```{text[::-1]}```")


@bot.command(description="Mocks text sending it lIkE tHiS.")
async def mock(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    mocked_text = "".join(
        char.upper() if i % 2 == 0 else char.lower() for i, char in enumerate(text)
    )

    await ctx.message.edit(content=f"{mocked_text}")


@bot.command(description="Adds a clap emoji between each word.")
async def clap(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(content=f"{text.replace(' ', ' :clap: ')} :clap:")


@bot.command(description="Converts your text to binary.")
async def text2bin(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(
        content=f"```{' '.join(format(ord(char), 'b') for char in text)}```"
    )


@bot.command(description="Converts binary to text.")
async def bin2text(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    try:
        await ctx.message.edit(
            content=f"```{''.join(chr(int(binary, 2)) for binary in text.split())}```"
        )
    except:
        await ctx.message.edit(content=":x: | Invalid binary text.")

        await delete_after_timeout(ctx.message)
        return


@bot.command(description="Converts your text to hex.")
async def text2hex(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    await ctx.message.edit(
        content=f"```{' '.join(hex(ord(char))[2:] for char in text)}```"
    )


@bot.command(description="Converts hex to text.")
async def hex2text(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    try:
        await ctx.message.edit(
            content=f"```{''.join(chr(int(hex, 16)) for hex in text.split())}```"
        )
    except:
        await ctx.message.edit(content=":x: | Invalid hex text.")

        await delete_after_timeout(ctx.message)
        return


@bot.command(description="Converts your text to morse code.")
async def morse(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    morse_code = {
        "a": ".-",
        "b": "-...",
        "c": "-.-.",
        "d": "-..",
        "e": ".",
        "f": "..-.",
        "g": "--.",
        "h": "....",
        "i": "..",
        "j": ".---",
        "k": "-.-",
        "l": ".-..",
        "m": "--",
        "n": "-.",
        "o": "---",
        "p": ".--.",
        "q": "--.-",
        "r": ".-.",
        "s": "...",
        "t": "-",
        "u": "..-",
        "v": "...-",
        "w": ".--",
        "x": "-..-",
        "y": "-.--",
        "z": "--..",
        " ": "/",
    }

    await ctx.message.edit(
        content=f"```{' '.join(morse_code[char.lower()] for char in text)}```"
    )


@bot.command(description="Converts your text to regional indicators.")
async def emojify(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    emojified_text = "".join(
        f":regional_indicator_{char.lower()}:" if char.isalpha() else char
        for char in text
    )

    await ctx.message.edit(content=f"{emojified_text}")


@bot.command(description="Converts morse code to text.")
async def unmorse(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    morse_code = {
        ".-": "a",
        "-...": "b",
        "-.-.": "c",
        "-..": "d",
        ".": "e",
        "..-.": "f",
        "--.": "g",
        "....": "h",
        "..": "i",
        ".---": "j",
        "-.-": "k",
        ".-..": "l",
        "--": "m",
        "-.": "n",
        "---": "o",
        ".--.": "p",
        "--.-": "q",
        ".-.": "r",
        "...": "s",
        "-": "t",
        "..-": "u",
        "...-": "v",
        ".--": "w",
        "-..-": "x",
        "-.--": "y",
        "--..": "z",
        "/": " ",
    }

    await ctx.message.edit(
        content=f"```{''.join(morse_code[char] for char in text.split())}```"
    )


@bot.command(aliases=["vaporise", "vaporize"], description="Vaporwave-ifies your text.")
async def vaporwave(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    vaporwave_text = "".join(f"{char}" if char == " " else f" {char} " for char in text)

    await ctx.message.edit(content=f"{vaporwave_text}")


@bot.command(aliases=["owoify"], description="OwO-ifies your text.")
async def owo(ctx, *, text: str = None):
    if text is None:
        await ctx.message.edit(content=":x: | No text provided.")

        await delete_after_timeout(ctx.message)
        return

    owo_text = (
        text.replace("r", "w").replace("l", "w").replace("R", "W").replace("L", "W")
    )

    await ctx.message.edit(content=f"{owo_text}")


####################################### Selfbot Settings #####################################


@bot.command(aliases=["setprefix"], description="Changes the selfbot's prefix.")
async def prefix(ctx, prefix: str = None):
    await ctx.message.edit(content="Changing prefix...")

    if prefix is None:
        await ctx.message.edit(content=":x: | No prefix provided.")

        await delete_after_timeout(ctx.message)
        return

    with open("config.json", "r") as f:
        config = json.load(f)

    config["prefix"] = prefix

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.message.edit(
        content=f":white_check_mark: | Changed prefix to `{prefix}` - Restarting..."
    )

    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.command(description="Shuts down the selfbot.")
async def shutdown(ctx):
    await ctx.message.edit(content="Shutting down...")

    log_message("shutdown", "Avarice Selfbot shutting down.", Fore.RED)

    await bot.close()

    os._exit(0)


@bot.command(aliases=["reboot"], description="Restarts the selfbot.")
async def restart(ctx):
    await ctx.message.edit(content="Restarting...")

    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.command(description="Changes how long it takes for messages to be auto deleted.")
async def deletetimer(ctx, timer: int = None):
    await ctx.message.edit(content="Deleting timer...")

    if timer is None:
        await ctx.message.edit(content=":x: | No time provided.")

        await delete_after_timeout(ctx.message)
        return

    with open("config.json", "r") as f:
        config = json.load(f)

    config["delete_timeout"] = timer

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.message.edit(
        content=f":white_check_mark: | Changed delete timeout to `{timer}` seconds. Restarting..."
    )

    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.command(
    aliases=["setafkmessage", "setafkmsg", "afkmsg"],
    description="Sets your AFK message.",
)
async def afkmessage(ctx, *, message: str = None):
    await ctx.message.edit(content="Setting AFK message...")

    if message is None:
        await ctx.message.edit(content=":x: | No message provided.")

        await delete_after_timeout(ctx.message)
        return

    with open("config.json", "r") as f:
        config = json.load(f)

    config["afk_message"] = message

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.message.edit(
        content=f":white_check_mark: | Set AFK message to `{message}`"
    )

    await delete_after_timeout(ctx.message)


@bot.command(description="Spies on a user, notifies you of all their activties.")
async def spy(ctx, user: discord.User = None):
    await ctx.message.edit(content="Spying on user...")

    if user is None:
        await ctx.message.edit(content=":x: | No user provided.")
        log_message("spy", f"No user provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    spyList.append(user.id)

    await ctx.message.edit(content=f":white_check_mark: | Now spying on `{user}`")

    await delete_after_timeout(ctx.message)


@bot.command(description="Stops spying on a user.")
async def unspy(ctx, user: discord.User = None):
    await ctx.message.edit(content="Unspying on user...")

    if user is None:
        await ctx.message.edit(content=":x: | No user provided.")
        log_message("unspy", f"No user provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    spyList.remove(user.id)

    await ctx.message.edit(content=f":white_check_mark: | No longer spying on `{user}`")

    await delete_after_timeout(ctx.message)


@bot.command(description="Sends how long the bot has been online.")
async def uptime(ctx):
    current_time = datetime.datetime.utcnow()
    uptime = current_time - startTime
    days, hours, minutes, seconds = (
        uptime.days,
        uptime.seconds // 3600,
        (uptime.seconds // 60) % 60,
        uptime.seconds % 60,
    )

    await ctx.message.edit(
        content=f"""```ini
[ Uptime ]

{days} days, {hours} hours, {minutes} minutes, {seconds} seconds```"""
    )


@bot.command(
    description="Edits the current server and sets it for your webhooks to allow notifications."
)
async def setupwebhooks(ctx):
    temp = await ctx.message.edit(content="Editing server...")

    guild = ctx.guild

    if not ctx.author.guild_permissions.administrator:
        await temp.edit(
            content=":x: | You need to have administrator permissions. Make sure you're running this command in your own server."
        )

        await delete_after_timeout(temp)
        return

    with open("data/avarice.png", "rb") as f:
        icon = f.read()

    await guild.edit(icon=icon)

    guild = bot.get_guild(guild.id)

    await asyncio.sleep(0.5)

    category = await guild.create_category("Avarice Logs")

    await asyncio.sleep(0.5)

    channel = await guild.create_text_channel("spy", category=category)
    webhook = await channel.create_webhook(name="Spy Logs", avatar=icon)

    with open("data/webhooks.txt", "w") as f:
        f.write("")

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Spy: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("new-tickets", category=category)
    webhook = await channel.create_webhook(name="Ticket Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Tickets: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("message-logs", category=category)
    webhook = await channel.create_webhook(name="Message Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Message Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("relationship-logs", category=category)
    webhook = await channel.create_webhook(name="Relationship Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Relationship Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("guild-logs", category=category)
    webhook = await channel.create_webhook(name="Guild Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Guild Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("role-logs", category=category)
    webhook = await channel.create_webhook(name="Role Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Role Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("ping-logs", category=category)
    webhook = await channel.create_webhook(name="Ping Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Ping Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("ghostping-logs", category=category)
    webhook = await channel.create_webhook(name="Ghostping Logs", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Ghostping Logs: {webhook.url}\n")

    await asyncio.sleep(1)

    channel = await guild.create_text_channel("word-notifications", category=category)
    webhook = await channel.create_webhook(name="Word Notifications", avatar=icon)

    with open("data/webhooks.txt", "a") as f:
        f.write(f"Word Notifications: {webhook.url}\n")

    await temp.edit(
        content=":white_check_mark: | Setup webhook server and log channels."
    )

    log_message(
        "setupwebhooks",
        f"Successfully setup webhook server and logs.",
        Fore.GREEN,
    )

    load_config()

    await delete_after_timeout(ctx.message)


@bot.command(
    aliases=["logblacklist", "blacklistlog"],
    description="Blacklists a channel from message logs.",
)
async def messagelogsblacklist(ctx, channel: int):
    await ctx.message.edit(content="Blacklisting channel...")

    if channel is None:
        await ctx.message.edit(content=":x: | No channel provided.")
        log_message("messagelogsblacklist", f"No channel provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    with open("data/logsblacklist.txt", "a") as f:
        f.write(f"{channel}\n")

    await ctx.message.edit(content=f":white_check_mark: | Blacklisted `{channel}`")

    load_config()

    await delete_after_timeout(ctx.message)


@bot.command(description="Unblacklists a channel from message logs.")
async def unblacklist(ctx, channel: int = None):
    await ctx.message.edit(content="Unblacklisting channel...")

    if channel is None:
        await ctx.message.edit(content=":x: | No channel provided.")
        log_message("unblacklist", f"No channel provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    with open("data/logsblacklist.txt", "r") as f:
        channels = f.readlines()

    with open("data/logsblacklist.txt", "w") as f:
        for line in channels:
            if line.strip("\n") != str(channel):
                f.write(line)

    await ctx.message.edit(content=f":white_check_mark: | Unblacklisted `{channel}`")

    await delete_after_timeout(ctx.message)


@bot.command(description="Turn on or off word notification logs.")
async def wordnotifications(ctx, status: str = None):
    status = status.lower()

    if status is None:
        await ctx.message.edit(content=":x: | No status provided.")
        log_message("wordnotifications", f"No status provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    if status == "on":
        config["wordNotifications"] = "True"

        with open("config.json", "w") as f:
            json.dump(config, f)

        load_config()

        await ctx.message.edit(
            content=":white_check_mark: | Turned on word notifications."
        )

        await delete_after_timeout(ctx.message)
    elif status == "off":
        config["wordNotifications"] = "False"

        with open("config.json", "w") as f:
            json.dump(config, f)

        load_config()

        await ctx.message.edit(
            content=":white_check_mark: | Turned off word notifications."
        )

        await delete_after_timeout(ctx.message)
    else:
        await ctx.message.edit(content=":x: | Invalid status provided.")

        log_message(
            "wordnotifications",
            f"Invalid status provided, please put either `on` or `off`.",
            Fore.RED,
        )

        await delete_after_timeout(ctx.message)


@bot.command(description="Add a word to the word notifications list.")
async def notifywords(ctx, word: str = None):
    await ctx.message.edit(content="Adding word...")

    if word is None:
        await ctx.message.edit(content=":x: | No word provided.")
        log_message("notifyWords", f"No word provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    notifyWords = config["notificationWords"]

    if word in notifyWords:
        notifyWords.remove(word)

        config["notificationWords"] = notifyWords

        with open("config.json", "w") as f:
            json.dump(config, f)

        await ctx.message.edit(content=f":white_check_mark: | Removed `{word}`")

    else:
        notifyWords.append(word)

        config["notificationWords"] = notifyWords

        with open("config.json", "w") as f:
            json.dump(config, f)

        await ctx.message.edit(content=f":white_check_mark: | Added `{word}`")

    load_config()

    await delete_after_timeout(ctx.message)


@bot.command(description="Turn on or off webhook logs.")
async def webhooklogs(ctx, status: str = None):
    status = status.lower()

    if status is None:
        await ctx.message.edit(content=":x: | No status provided.")
        log_message("webhooklogs", f"No status provided.", Fore.RED)

        await delete_after_timeout(ctx.message)
        return

    if status == "on":
        config["webhooks"] = "True"

        with open("config.json", "w") as f:
            json.dump(config, f)

        load_config()

        await ctx.message.edit(content=":white_check_mark: | Turned on webhooks.")

        await delete_after_timeout(ctx.message)
    elif status == "off":
        config["webhooks"] = "False"

        with open("config.json", "w") as f:
            json.dump(config, f)

        load_config()

        await ctx.message.edit(content=":white_check_mark: | Turned off webhooks.")

        await delete_after_timeout(ctx.message)
    else:
        await ctx.message.edit(
            content=":x: | Invalid status provided. Valid statuses: `on`, `off`."
        )
        log_message(
            "webhooklogs",
            "Invalid status provided.",
            Fore.RED,
        )

        await delete_after_timeout(ctx.message)
        return

    await delete_after_timeout(ctx.message)


@bot.command(aliases=["about", "info"], description="Shows information about the bot.")
async def avarice(ctx):
    response = requests.get("https://avariceapi.najmul190.repl.co/api/user/count")
    user_count = response.json()["user_count"]

    response = requests.get(
        "https://avariceapi.najmul190.repl.co/api/user/unique_count"
    )
    uniqueUserCount = response.json()["unique_user_count"]

    if user_count is None:
        user_count = "Unknown"

    current_time = datetime.datetime.utcnow()
    uptime = current_time - startTime

    days, hours, minutes, seconds = (
        uptime.days,
        uptime.seconds // 3600,
        (uptime.seconds // 60) % 60,
        uptime.seconds % 60,
    )

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot
                           
[Version] {currentVersion}

[Global Logins] {user_count}
[Unique Logins] {uniqueUserCount}

[Commands] {len(bot.commands)}
[Uptime] {days}d:{hours}h:{minutes:02}m:{seconds:02}s

[Creator] https://github.com/Najmul190 | @najmul (451627446941515817)
[Link] https://github.com/Najmul190/Avarice-Selfbot```"""
    )


bot.remove_command("help")


@bot.command(description="Shows this message.")
async def help(ctx, command: str = None):
    prefix = config["prefix"]

    if command is None:
        await ctx.message.edit(
            content=f"""```ini
Avarice Selfbot | Prefix: {prefix}

[{prefix}moderation] Moderation commands
[{prefix}utilities] Utility commands
[{prefix}tools] General tools
[{prefix}troll] Trolling commands
[{prefix}raid] Raiding commands (use at your own risk)
[{prefix}fun] Commands designed for fun
[{prefix}nsfw] NSFW commands
[{prefix}animated] Animated commands
[{prefix}text] Text commands, make your text look cool
[{prefix}settings] Settings commands
[{prefix}avarice] Show information about the selfbot
```"""
        )

        await delete_after_timeout(ctx.message)

    else:
        command = bot.get_command(command)

        if command:
            aliases = str(command.aliases)
            aliases = aliases.replace("[", "")
            aliases = aliases.replace("]", "")
            aliases = aliases.replace("'", "")

            await ctx.message.edit(
                content=f"""```markdown
Avarice Selfbot | {command.name} | Prefix: {prefix}

[Description] {command.description}
[Usage] {prefix}{command.name} {command.signature}
[Aliases] {aliases}
```"""
            )

            await delete_after_timeout(ctx.message)

        else:
            await ctx.message.edit(content=":x: | Command not found.")

            await delete_after_timeout(ctx.message)


@bot.command(description="Shows the moderation commands.")
async def moderation(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Moderation Commands | Prefix: {prefix}

[{prefix}createtext] Create a text channel
[{prefix}createvoice] Create a voice channel
[{prefix}forcenick] Keep changing a user's nickname so it remains permanent
[{prefix}stopforcenick] Stop forcing a user to change their nickname
[{prefix}nick] Change a user's nickname
[{prefix}purge] Purge an amount of messages
[{prefix}purgeuser] Purge a user's messages
[{prefix}purgecontains] Purge messages that contain a certain word
[{prefix}clean] Purges your own messages
[{prefix}kick] Kick a user
[{prefix}ban] Ban a user
[{prefix}unban] Unban a user
[{prefix}exportbans] Export a server's bans in ID format
[{prefix}importbans] Import bans from another server
[{prefix}timeout] Timeout a user
[{prefix}untimeout] Untimeout a user
[{prefix}slowmode] Set a channel's slowmode
[{prefix}nuke] Nuke a channel, cloning it and deleting the old one
[{prefix}roleall] Give a role to all members
[{prefix}removeroleall] Remove a role from all members
[{prefix}giveallroles] Give every role in the server to a user
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def utilities(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Utility Commands | Prefix: {prefix}

[{prefix}firstmessage] Get the first message in a channel
[{prefix}dmtoken] DM a user with your token
[{prefix}playing] Set your playing status
[{prefix}watching] Set your watching status
[{prefix}listening] Set your listening status
[{prefix}streaming] Set your streaming status
[{prefix}removepresence] Remove your presence
[{prefix}cycleplaying] Cycle through a list of playing statuses
[{prefix}stopcycleplaying] Stop cycling through playing statuses
[{prefix}cyclewatching] Cycle through a list of watching statuses
[{prefix}stopcyclewatching] Stop cycling through watching statuses
[{prefix}cyclelistening] Cycle through a list of listening statuses
[{prefix}stopcyclelistening] Stop cycling through listening statuses
[{prefix}cyclestreaming] Cycle through a list of streaming statuses
[{prefix}stopcyclestreaming] Stop cycling through streaming statuses
[{prefix}online] Set your status to online
[{prefix}idle] Set your status to idle
[{prefix}dnd] Set your status to do not disturb
[{prefix}invisible] Set your status to invisible
[{prefix}leaveallgroups] Leave all groups you're in
[{prefix}leaveallservers] Leave all guilds you're in
[{prefix}stopleave] Stop leaving all guilds or groups
[{prefix}nickloop] Loop through a list of nicknames
[{prefix}stopnickloop] Stop looping through nicknames
[{prefix}setpfp] Set your profile picture
[{prefix}deletewebhook] Delete a webhook
[{prefix}hypesquad] Set your hypesquad house
[{prefix}status] Cycle status through time, different statuses, text or clear
[{prefix}afk] Set your status to afk
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def tools(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | General Tools | Prefix: {prefix}

[{prefix}tokeninfo] Get information about a token
[{prefix}userinfo] Get information about a user
[{prefix}serverinfo] Get information about a server
[{prefix}inviteinfo] Get information about an invite
[{prefix}serverfriends] Get a list of your friends in a server
[{prefix}ipinfo] Get information about an IP address
[{prefix}mutualservers] Get a list of servers you share with a user
[{prefix}mutualfriends] Get a list of friends you share with a user
[{prefix}roleinfo] Get information about a role
[{prefix}snipe] Snipe the last deleted message
[{prefix}editsnipe] Snipe the last edited message
[{prefix}adminservers] Get a list of servers you're an admin in
[{prefix}revavatar] Reverse image search a users avatar
[{prefix}autobumper] Automatically bump a server every 2 hours
[{prefix}stopbumper] Stop automatically bumping a server
[{prefix}autoslashcommand] Automatically use a slash command with a delay
[{prefix}autocommand] Automatically use a command with a delay
[{prefix}stopautoslashcommand] Stop automatically using a slash command
[{prefix}stopautocommand] Stop automatically using a command
[{prefix}dumpembed] Dump the latest embed from a channel to json
[{prefix}dumpchat] Dump an amount of messages from a channel to a txt file
[{prefix}dm] DM a user with a message
[{prefix}cryptotransaction] Get information about a crypto transaction
[{prefix}nickscan] Lists all the nicknames you have in all servers
[{prefix}nickreset] Reset your nickname in all servers
[{prefix}addemoji] Add an emoji to a server
[{prefix}allowaddemoji] Allow a user to add an emoji to a server by sending the emoji
[{prefix}emojidelete] Delete an emoji from a server
[{prefix}dumpattachments] Dump an amount of attachments from a channel into a txt file
[{prefix}downloadattachments] Download a certain amount of attachments from a channel
[{prefix}roles] Get a list of roles in a server
[{prefix}roleperms] Get a list of permissions for a role
[{prefix}userbio] Get a user's bio
[{prefix}banner] Get a user's banner
[{prefix}scrapemembers] Scrape all members from a server and save them to a txt file
[{prefix}scrapepfps] Scrape all pfps from a server and save them to a txt file
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def troll(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Troll Commands | Prefix: {prefix}

[{prefix}empty] Send an empty message
[{prefix}purgehack] Send a bunch of empty messages to seemingly clear a channel
[{prefix}ghostping] Ghost ping a user in a channel
[{prefix}hiddenping] Ping a user in a channel, using an exploit to hide the ping
[{prefix}hiddenpingeveryone] Ping everyone in a channel, using an exploit to hide the ping
[{prefix}hiddeninvite] Send an invite to a server, using an exploit to hide the invite
[{prefix}ghostpingrole] Ghost ping a role in a channel, using an exploit to hide the ping
[{prefix}stealpfp] Steal a users pfp
[{prefix}invispfp] Set your profile picture to a transparent image
[{prefix}pingmute] Mutes any users that pings you
[{prefix}stoppingmute] Stop muting users that ping you
[{prefix}pingkick] Kicks any users that ping you
[{prefix}stoppingkick] Stop kicking users that ping you
[{prefix}pingrole] Gives any users that ping you a role
[{prefix}stoppingrole] Stop giving users that ping you a role
[{prefix}mimic] Mimic a user, copying each message they send
[{prefix}stopmimic] Stop mimicking a user
[{prefix}smartmimic] Mimic a user, copying each message they send bUt iTs LiKe ThIs
[{prefix}stopsmartmimic] Stop mimicking a user
[{prefix}addwhitelist] Add a server to the whitelist for the pingmute, pingkick, and pingrole commands
[{prefix}removewhitelist] Remove a server from the whitelist for the pingmute, pingkick, and pingrole commands
[{prefix}noleave] Forces a user to stay in a group, not allowing them to leave
[{prefix}allowleave] Allow a user to leave a group
[{prefix}grouplag] Lag a group voice channel by mass changing region
[{prefix}stopgrouplag] Stop lagging a group voice channel
[{prefix}pinspam] Pin every message a user sends
[{prefix}stoppinspam] Stop pinning every message a user sends
[{prefix}deleteannoy] Delete every message a user sends
[{prefix}stopdeleteannoy] Stop deleting every message a user sends
[{prefix}reactuser] React to every message a user sends
[{prefix}stopreactuser] Stop reacting to every message a user sends
[{prefix}forcedisconnect] Keep disconnecting a user from a voice channel
[{prefix}stopforcedisconnect] Stop forcefully disconnecting a user from a voice channel
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def raid(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Raid Commands | Prefix: {prefix}

[{prefix}banall] Ban all members in a server
[{prefix}unbanall] Unban all members in a server
[{prefix}massmention] Keep mentioning loads of users in a channel
[{prefix}deletechannels] Delete all channels in a server
[{prefix}deleteroles] Delete all roles in a server
[{prefix}deleteemojis] Delete all emojis in a server
[{prefix}deletestickers] Delete all stickers in a server
[{prefix}nukeserver] Delete all channels, roles, emojis, and stickers in a server
[{prefix}webhookspam] Creates a webhook in every channel and spams the message provided in config.json
[{prefix}stopwebhookspam] Stop spamming the webhooks
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def fun(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Fun Commands | Prefix: {prefix}

[{prefix}chatbot] Talk to an AI powered by ChatGPT for free
[{prefix}imagine] Generate an image using AI
[{prefix}halftoken] Get half of a users token
[{prefix}nsfw] A bunch of NSFW commands
[{prefix}iq] Get a users IQ
[{prefix}dick] Get the dick size of a user
[{prefix}8ball] Ask the magic 8ball a question
[{prefix}kiss] Kiss a user with a gif
[{prefix}hug] Hug a user with a gif
[{prefix}pat] Pat a user with a gif
[{prefix}slap] Slap a user with a gif
[{prefix}tickle] Tickle a user with a gif
[{prefix}cuddle] Cuddle a user with a gif
[{prefix}feed] Feed a user with a gif
[{prefix}triggertyping] Trigger typing in a channel
[{prefix}massreact] React with an emoji to an amount of messages
[{prefix}slots] Play a game of slots
[{prefix}spam] Spam a message in a channel an amount of times
[{prefix}poll] Create a poll in a channel
[{prefix}coinflip] Flip a coin
[{prefix}randomnumber] Get a random number
[{prefix}rps] Play rock paper scissors
[{prefix}dice] Roll a dice
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def animated(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Animated Text Commands | Prefix: {prefix}

[{prefix}fuckyou] Sends an animated 'fuck you' message pinging a user
[{prefix}count] Count to 100 in a message
[{prefix}abc] Write the whole alphabet in a message
[{prefix}virus] Send an animated virus of your choice
[{prefix}readrules] Tell a user to read the fucking rules
[{prefix}warning] Send an animated warning message
[{prefix}bomb] Send an animated bomb message
[{prefix}wank] Send an animated wanking message
```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def text(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Animated Text Commands | Prefix: {prefix}

[{prefix}encode] Encode a message using base64
[{prefix}decode] Decode a base64 message
[{prefix}reverse] Reverse a string
[{prefix}mock] Make text come out in a mocked manner
[{prefix}clap] Add a clap between every word
[{prefix}text2bin] Text to binary
[{prefix}bin2text] Binary to text
[{prefix}text2hex] Text to hexadecimal
[{prefix}morse] Text to morse code
[{prefix}unmore] Morse code to text
[{prefix}emojify] Emojifies your text into regional indicators
[{prefix}vaporwave] m  a  k  e   y  o  u  r   t  e  x  t   l  i  k  e   t  h  i  s
[{prefix}owo] makes youw text wike this```"""
    )

    await delete_after_timeout(ctx.message)


@bot.command()
async def settings(ctx):
    prefix = config["prefix"]

    await ctx.message.edit(
        content=f"""```ini
Avarice Selfbot | Settings Commands | Prefix: {prefix}

[{prefix}prefix] Change the prefix of the selfbot
[{prefix}shutdown] Shutdown the selfbot
[{prefix}deletetimer] Configure the delete timer for messages
[{prefix}afkmessage] Set your AFK message
[{prefix}spy] Spy on a user, getting notified on everything they do
[{prefix}unspy] Stop spying on a user
[{prefix}uptime] Get the uptime of the selfbot
[{prefix}setupwebhooks] Setup your webhooks server for notifications
[{prefix}messagelogsblacklist] Blacklist a channel from message logs
[{prefix}unblacklist] Unblacklist a channel from message logs
[{prefix}wordnotifications] Enable or disable word notifications
[{prefix}notifywords] Add or remove words from the word notifications
[{prefix}webhooklogs] Enable or disable webhook logs```"""
    )

    await delete_after_timeout(ctx.message)


####################################### Error Handling #######################################

if config["debugMode"] == "False":

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.message.edit(content=":x: | Command not found.")
            log_message("Avarice Error", error, Fore.RED)
            await delete_after_timeout(ctx.message)

        elif isinstance(error, discord.errors.NotFound):
            log_message("Avarice Error", error, Fore.RED)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.message.edit(content=f":x: | Missing required argument: {error}")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.BadArgument):
            await ctx.message.edit(content=f":x: | Bad argument: {error}")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.MissingPermissions):
            await ctx.message.edit(content=":x: | Missing permissions.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.BadInviteArgument):
            await ctx.message.edit(
                content=":x: | Bad invite argument. May be expired or invalid."
            )
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.message.edit(content=":x: | Bot missing permissions.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.MissingRole):
            await ctx.message.edit(content=":x: | Missing role.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.message.edit(content=":x: | Command disabled.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.TooManyArguments):
            await ctx.message.edit(content=":x: | Too many arguments.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.UserInputError):
            await ctx.message.edit(content=":x: | User input error.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.MemberNotFound):
            await ctx.message.edit(content=":x: | Member not found.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.UserNotFound):
            await ctx.message.edit(content=":x: | User not found.")
            await delete_after_timeout(ctx.message)

        elif isinstance(error, commands.CommandError):
            await ctx.message.edit(content=":x: | Command error.")
            log_message("Avarice Error", error, Fore.RED)

            try:
                await delete_after_timeout(ctx.message)
            except:
                pass

        elif isinstance(error, commands.CheckFailure):
            await ctx.message.edit(content=":x: | Check failure.")
            await delete_after_timeout(ctx.message)


try:
    if config["debugMode"] == "True":
        bot.run(config["token"])
    else:
        bot.run(config["token"], log_handler=None)

except discord.errors.HTTPException:
    log_message("Token Error", "Invalid token set in config.json.", Fore.RED)

    TOKEN = input("Enter a valid token: ")

    config["token"] = TOKEN

    with open("config.json", "w") as f:
        json.dump(config, f)

    os.execl(sys.executable, sys.executable, *sys.argv)

except discord.errors.LoginFailure:
    log_message("Token Error", "Invalid token set config.json.", Fore.RED)

    TOKEN = input("Enter a valid token: ")

    config["token"] = TOKEN

    with open("config.json", "w") as f:
        json.dump(config, f)

    os.execl(sys.executable, sys.executable, *sys.argv)
