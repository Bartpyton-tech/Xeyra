import discord
from discord import app_commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv
import logging
from flask import Flask
import threading

# ===== LOGI =====
logging.basicConfig(level=logging.INFO)

# ===== ENV =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ===== INTENTS =====
intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ===== FLASK (RENDER) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ===== GUILD =====
GUILD_ID = 1410955423648845825  # <-- ID SERWERA

# ===== READY =====
@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    logging.info(f"Zalogowano jako {client.user}")

# ===== VIEW Z PRZYCISKIEM =====
class RollbackView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Utwórz kanał",
        style=discord.ButtonStyle.primary,
        emoji="➕"
    )
    async def create_channel(self, interaction: discord.Interaction, button: Button):

        guild = interaction.guild
        member = interaction.user

        # 👉 PRAWDZIWA NAZWA Z DISCORDA (nick > username)
        display_name = member.display_name.lower().replace(" ", "-")

        channel_name = f"rollback-{display_name}"

        # sprawdź czy kanał już istnieje
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(
                f"❌ Kanał **{channel_name}** już istnieje.",
                ephemeral=True
            )
            return

        channel = await guild.create_text_channel(channel_name)

        await channel.send(
            f"🎥 **Rollback dla {member.mention}**\n"
            "Wrzuć tutaj klipa + timecodes."
        )

        await interaction.response.send_message(
            f"✅ Utworzono kanał {channel.mention}",
            ephemeral=True
        )

# ===== KOMENDA =====
@tree.command(
    name="rollbackstworz",
    description="Tworzy rollback z przyciskiem",
    guild=discord.Object(id=GUILD_ID)
)
async def rollbackstworz(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔧 Rollback",
        description=(
            "**Na czym polega rollback?**\n"
            "Tworzysz kanał, wrzucasz klipa + timecodes,\n"
            "a my pomagamy Ci się poprawić.\n\n"
            "**Kliknij przycisk poniżej, aby utworzyć kanał.**"
        ),
        color=0x7B3FE4
    )

    await interaction.response.send_message(
        embed=embed,
        view=RollbackView()
    )

# ===== START =====
client.run(TOKEN)




