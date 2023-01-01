#!/usr/bin/env python3

import discord
from discord import app_commands
from discord.ext import commands



class Variety(commands.Cog):
	@app_commands.command()
	@app_commands.guilds(862318231472701460) # Restricts the command to the Variety.TF server
	async def playtest(self, interaction: discord.Interaction):
		role = interaction.guild.get_role(1058765060119465994)
		await interaction.user.add_roles(role, reason="Member used the /playtest command.")
		await interaction.response.send_message(f"You now have the {role.mention} role. Thanks for helping out!", ephemeral=True)
