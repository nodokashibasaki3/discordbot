import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import csv
import io
import os

TOKEN = os.getenv("TOKEN")
CSV_URL = os.getenv("CSV_URL")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

async def fetch_cabin_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(CSV_URL) as resp:
            if resp.status != 200:
                return {}
            data = await resp.text()
            reader = csv.DictReader(io.StringIO(data))
            cabin_map = {}
            for row in reader:
                username = row["Discord Username"].strip().lower()
                cabin = row["Cabin"].strip()
                role = row["Role"].strip().lower()
                cabin_map[username] = {"cabin": cabin, "role": role}
            return cabin_map

@tree.command(name="assign_me", description="Assigns your preassigned cabin role and gives access to team channels.")
async def assign_me(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    username = interaction.user.name.lower()
    cabin_data = await fetch_cabin_data()

    if username not in cabin_data:
        await interaction.followup.send("You're not on the cabin list.")
        return

    user_info = cabin_data[username]
    cabin_name = user_info["cabin"]
    user_role = user_info["role"]

    guild = interaction.guild
    member = interaction.user

    # Assign cabin role
    matching_roles = [r for r in guild.roles if r.name.lower() == cabin_name.lower()]
    if not matching_roles:
        await interaction.followup.send(f"Role '{cabin_name}' not found.")
        return
    cabin_role = matching_roles[0]
    await member.add_roles(cabin_role)

    # Create or fetch cabin chat
    channel_name = f"cabin-{cabin_name.lower().replace(' ', '-')}-chat"
    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not existing_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            cabin_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        new_channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason=f"Cabin chat for {cabin_name}"
        )
    else:
        new_channel = existing_channel

    if user_role == "leader":
        matching_leader_roles = [r for r in guild.roles if r.name.lower() == "leader"]
        if matching_leader_roles:
            leader_role = matching_leader_roles[0]
        else:
            leader_role = await guild.create_role(name="Leader", reason="Auto-created Leader role")

        leader_channel = discord.utils.get(guild.text_channels, name="leaders-hub")
        if not leader_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                leader_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
            leader_channel = await guild.create_text_channel(
                name="leaders-hub",
                overwrites=overwrites,
                reason="Global Leader Hub"
            )
        else:
            leader_channel = discord.utils.get(guild.text_channels, name="leaders-hub")

        await interaction.followup.send(
            f"Assigned to **{cabin_name}** as **Leader**.\n"
            f"Cabin chat: <#{new_channel.id}>\n"
            f"Leader hub: <#{leader_channel.id}>",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            f"Assigned to **{cabin_name}** as **Member**.\n"
            f"Cabin chat: <#{new_channel.id}>",
            ephemeral=True
        )

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)
