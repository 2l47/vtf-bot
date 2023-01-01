#!/usr/bin/env python3

import discord
from discord.ext import commands
import textwrap



class Functions(commands.Cog):
	@commands.command()
	@commands.is_owner()
	async def restart(self, ctx):
		"""Restarts the bot. Only the bot owner can use this command."""

		await ctx.send("Restarting.")
		game = discord.Game(name="Restarting...")
		await ctx.bot.change_presence(status=discord.Status.dnd, activity=game)
		await ctx.bot.close(shutdown=False)


	@commands.command()
	@commands.is_owner()
	async def shutdown(self, ctx):
		"""Shuts down the bot. Only the bot owner can use this command."""

		await ctx.send("Shutting down.")
		game = discord.Game(name="Shutting down...")
		await ctx.bot.change_presence(status=discord.Status.invisible, activity=game)
		await ctx.bot.close(shutdown=True)


	async def can_purge(ctx):
		if ctx.message.author == ctx.bot.owner:
			return True
		if type(ctx.message.channel) != discord.DMChannel:
			if ctx.message.author == ctx.message.guild.owner:
				return True
		return False


	@commands.command()
	@commands.guild_only()
	@commands.check(can_purge)
	async def purge(self, ctx, number):
		"""Deletes a given number of messages. Only the server or bot owner can use this command."""

		number = int(number)
		deleted_messages = await ctx.channel.purge(limit=number)
		await ctx.send(f"Purged {len(deleted_messages)} messages.", delete_after=5.0)


	@commands.command()
	@commands.guild_only()
	@commands.check(can_purge)
	async def purge_from_to(self, ctx, first_message_id, last_message_id):
		"""Deletes all messages between two message IDs. Only the server or bot owner can use this command."""

		first_message_id = discord.Object(int(first_message_id))
		last_message_id = discord.Object(int(last_message_id))
		deleted_messages = await ctx.channel.purge(limit=1000, after=first_message_id, before=last_message_id)
		await ctx.send(f"Purged {len(deleted_messages)} messages.")


	@commands.command()
	@commands.guild_only()
	@commands.check(can_purge)
	async def purge_user(self, ctx, user, number): # TODO
		"""
		Deletes a number of a given user's messages. Only the server or bot owner can use this command.

		Example usage:
			-purge_user Wumpus 20
		"""

		#await ctx.channel.purge()
		raise RuntimeError("Not implemented.")


	def get_code(self, ctx):
		code = ctx.message.content

		start = code.find("```python\n") + 10
		code = code[start:]

		end = code.find("```")
		code = code[:end]
		return code.strip("\n")


	@commands.command()
	@commands.is_owner()
	async def raw_exec(self, ctx):
		"""
		Executes arbitrary python code. Only the bot owner can use this command.

		Use backticks (`) for the code block, not single quotes (').
		Example message content:
			!raw_exec
			'''python
			import asyncio
			async def example_function(ctx):
				await ctx.send("Hello, world!")
			ctx.bot.loop.create_task(example_function(ctx))
			'''
		"""

		exec(self.get_code(ctx))


	@commands.command()
	@commands.is_owner()
	async def exec(self, ctx):
		"""
		Wraps the code you want to exec for ease of use. Only the bot owner can use this command.

		Use backticks (`) for the code block, not single quotes (').
		Example message content:
			!exec
			'''python
			await ctx.send("Hello, world!")
			'''
		"""

		user_code = self.get_code(ctx)
		indented_code = ""
		for line in user_code.split("\n"):
			indented_code += f"\t{line}\n"
		indented_code = indented_code[:-1] # Remove the trailing newline

		code = textwrap.dedent("""
		async def owner_exec(ctx):
			await ctx.send("Task created.")
			bot = ctx.bot # alias

		{}

			await ctx.reply("Code finished executing.", delete_after=15.0)


		ctx.bot.loop.create_task(owner_exec(ctx))
		""").format(indented_code)

		await ctx.send(f"Executing code: \n```python\n{code}\n```")
		exec(code)
