# bot.py
import discord
from discord.ext import commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

bot = commands.Bot(command_prefix="!", intents=INTENTS, help_command=None)

# -------------------------------
# DANE ZBIÓREK
# -------------------------------
zbiorki = {}  # {message_id: {limit: int, activity: str, users: [], channel: id}}

# -------------------------------
# VIEW DO PRZYCISKÓW
# -------------------------------
class ZbiorkaView(View):
    def __init__(self, limit, activity):
        super().__init__(timeout=None)
        self.limit = limit
        self.activity = activity

    @discord.ui.button(label="Wpisz się", style=discord.ButtonStyle.blurple)
    async def wpisz(self, interaction: discord.Interaction, button: Button):
        data = zbiorki.get(interaction.message.id)

        if not data:
            return await interaction.response.send_message("Błąd zbiórki!", ephemeral=True)

        if interaction.user.id in data["users"]:
            return await interaction.response.send_message("Już jesteś zapisany!", ephemeral=True)

        if len(data["users"]) >= data["limit"]:
            return await interaction.response.send_message("Brak miejsc!", ephemeral=True)

        data["users"].append(interaction.user.id)
        await update_zbiorka_embed(interaction.message)
        await interaction.response.send_message("Zapisano!", ephemeral=True)

    @discord.ui.button(label="Wypisz się", style=discord.ButtonStyle.gray)
    async def wypisz(self, interaction: discord.Interaction, button: Button):
        data = zbiorki.get(interaction.message.id)

        if interaction.user.id not in data["users"]:
            return await interaction.response.send_message("Nie jesteś zapisany!", ephemeral=True)

        data["users"].remove(interaction.user.id)
        await update_zbiorka_embed(interaction.message)
        await interaction.response.send_message("Wypisano!", ephemeral=True)

    @discord.ui.button(label="Administracja", style=discord.ButtonStyle.red)
    async def admin(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Panel admina — do rozszerzenia.", ephemeral=True)

# -------------------------------
# AKTUALIZACJA EMBEDA
# -------------------------------
async def update_zbiorka_embed(message):
    data = zbiorki[message.id]

    users_list = "\n".join([f"🟥 <@{u}> - ja" for u in data["users"]]) or "Brak zapisanych"

    embed = discord.Embed(
        title=data["activity"],
        description=f"Osoby które zostały wybrane ({len(data['users'])}/{data['limit']})\n\n{users_list}",
        color=0x2b2d31
    )

    await message.edit(embed=embed, view=ZbiorkaView(data["limit"], data["activity"]))

# -------------------------------
# KOMENDA ZBIÓRKA
# -------------------------------
@bot.command()
async def zbiorka(ctx, limit: int, *, activity: str):
    embed = discord.Embed(
        title=activity,
        description=f"Osoby które zostały wybrane (0/{limit})\n\nBrak zapisanych",
        color=0x2b2d31
    )

    view = ZbiorkaView(limit, activity)
    msg = await ctx.send(embed=embed, view=view)

    zbiorki[msg.id] = {
        "limit": limit,
        "activity": activity,
        "users": []
    }

    # Tworzenie kanału głosowego
    channel = await ctx.guild.create_voice_channel(activity)
    zbiorki[msg.id]["channel"] = channel.id

# -------------------------------
@bot.event
async def on_ready():
    print(f"Zalogowano jako: {bot.user}")

# -------------------------------
bot.run(TOKEN)
