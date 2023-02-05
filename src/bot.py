#!/usr/bin/env python3

import asyncio
import configparser
import discord
from discord.ext import commands
import logging
import os
import signal

from cogs.functions import Functions
from cogs.variety import Variety

logger = logging.getLogger("discord")
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error



# Is there an instance running already?
if os.path.exists("../state/bot.pid"):
	raise RuntimeError("An instance of bot.py is already running!")

# Write our PID to the file so we can kill the bot externally if necessary
with open("../state/bot.pid", "w") as f:
	f.write(str(os.getpid()))


# Custom Bot class for handling restarts and shutdowns
class Bot(commands.Bot):
	async def close(self, shutdown=False):
		"""|coro|

		Closes the connection to Discord.
		"""

		if shutdown and os.path.exists("../state/loop.pid"):
			f = open("../state/want_shutdown", "a")
			f.close()

		await super().close()


# Create an instance of the custom Bot class
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(command_prefix="!", intents=intents)

# Handle SIGTERM
def sigterm(signum, frame):
	# Always "SIGTERM" but eh
	signame = signal.Signals(signum).name
	warning(f"Caught {signame}, calling bot.close()")
	asyncio.create_task(bot.close(shutdown=False))
signal.signal(signal.SIGTERM, sigterm)

# Load our configuration
config = configparser.ConfigParser()
config.read("../config.ini")
cfg = config["config"]
token = cfg["token"]

# Initialization
bot.loaded_cogs = False


# Load stuff once we are connected
@bot.event
async def on_ready():
	info("Client is ready...")

	# Store the owner's User object for any future use
	application_info = await bot.application_info()
	bot.owner = application_info.owner

	# Store the preferred guild for logging
	for guild in bot.guilds:
		if guild.id == int(cfg["logging-guild"]):
			bot.logging_guild = guild
			for channel in guild.text_channels:
				if channel.id == int(cfg["logging-channel"]):
					bot.logging_channel = channel
					break
			break
	assert hasattr(bot, "logging_guild")
	assert hasattr(bot, "logging_channel")

	# Load in cogs
	if not bot.loaded_cogs:
		await bot.add_cog(Functions())
		await bot.add_cog(Variety())
		bot.loaded_cogs = True

		# Sync all global application commands
		info("Syncing global application commands...")
		global_synced = await bot.tree.sync()
		names = []
		for command in global_synced:
			names.append(command.name)
		names = ", ".join(names)
		info(f"Synced {len(global_synced)} global application command(s): {names}")

		# Sync all guild-specific application commands
		info("Syncing guild-specific application commands...")
		# Create a set of guild IDs which have application commands specific to that guild
		guild_ids = set()
		# bot.tree._guild_commands: {123: {'commandName': <discord.app_commands.commands.Command object>}}
		# bot.tree._guild_commands.values(): dict_values([{'commandName': <discord.app_commands.commands.Command object>}])
		for _dict in bot.tree._guild_commands.values():
			# _dict: {'commandName': <discord.app_commands.commands.Command object>}
			command_list = list(_dict.values())
			# command_list: [<discord.app_commands.commands.Command object]
			assert len(command_list) == 1
			command = command_list[0]
			if command._guild_ids is not None:
				for guild_id in command._guild_ids:
					guild_ids.add(guild_id)
		info(f"\t{bot.user.name} has guild-specific application commands in {len(guild_ids)} different guild(s).")
		# Now sync application commands for each of those guilds
		# Also, store the synced commands so we can count them afterwards
		guild_synced = set()
		for guild_id in guild_ids:
			# sync(guild=) expects a discord.abc.Snowflake, not an int :(
			synced = await bot.tree.sync(guild=discord.Object(guild_id))
			names = []
			for command in synced:
				names.append(command.name)
			names = ", ".join(names)
			guild = bot.get_guild(guild_id)
			info(f"\t\tSynced {len(synced)} application command(s) specific to guild [{guild}] (ID {guild_id}): {names}")
			for command in synced:
				guild_synced.add(command)
		names = []
		for command in guild_synced:
			names.append(command.name)
		names = ", ".join(names)
		info(f"Synced {len(guild_synced)} guild-specific application command(s): {names}")

	game = discord.Game(name="Team Fortress 2") # create our custom activity
	await bot.change_presence(status=discord.Status.online, activity=game) # set our status and activity
	info(f"{bot.user.name} is ready!\n")
	info(f"Here's my invite link: https://discordapp.com/oauth2/authorize?&client_id={bot.user.id}&scope=bot")


@bot.event
async def on_member_remove(member):
	await bot.logging_channel.send(
		f"{member} ({member.nick}) left or was kicked from `{member.guild.name}`."
	)


async def log_message(message):
	guild = message.guild # Can be None when the channel is a DM
	channel = message.channel
	author = message.author
	msg = message.clean_content

	# Log the message and its attachments to stdout
	formatted, attachments = None, ""
	if type(channel) == discord.DMChannel:
		recipient = "Unknown recipient"
		if channel.recipient:
			recipient = channel.recipient.name
		formatted = f"[DM with {recipient}] {author.name}: {msg}\n"
	else:
		formatted = f"[{guild.name}] #{channel.name}: {author}/{author.display_name}: {msg}\n"
	for index, item in enumerate(message.attachments):
		attachments += f"\tAttachment #{index}: {item.url}\n"
	info(formatted + attachments)

	# Log user DMs for debugging
	if type(channel) == discord.DMChannel:
		# Only log if the DM isn't with the bot owner
		if channel.recipient.id != bot.owner.id:
			await bot.logging_channel.send(formatted + attachments)


@bot.event
async def on_message(message):
	await log_message(message)

	# Ignore messages from self
	if message.author.id == bot.user.id:
		return

	# Process any bot commands for this message
	await bot.process_commands(message)


# Start the bot
print("\nStarting bot...")
try:
	bot.run(token)
except:
	raise
finally:
	# Bye
	os.remove("../state/bot.pid")
