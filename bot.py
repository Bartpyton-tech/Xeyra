import discord
from discord import app_commands
from discord.ui import View, Button
import os
from dotenv import load_dotenv
import logging
from flask import Flask
import threading

# ========= LOGI =========
logging.basicConfig(level=logging.INFO)

# ========= ENV =========
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ========= DISCORD =========
intents = discord.Intents.default()
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ========= RENDER / FLASK =========
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ========= USTAWIENIA =========
GUILD_ID = 1410955423648845825  # <<< ID TWOJEGO SERWERA

# ========= VIEW Z PRZYCISKIEM =========
class RollbackView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Utwórz kanał",
        style=discord.ButtonStyle.primary,
        emoji="🛠️"
    )
    async def create_channel(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        member = interaction.user

        channel_name = f"rollback-{member.name}".lower()

        # SPRAWDŹ CZY JUŻ ISTNIEJE
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(
                f"Masz już kanał {existing.mention}",
                ephemeral=True
            )
            return

        # ===== PRYWATNE UPRAWNIENIA =====
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            channel_name,
            overwrites=overwrites
        )

        await interaction.response.send_message(
            f"Utworzono kanał {channel.mention}",
            ephemeral=True
        )

# ========= READY =========
@client.event
async def on_ready():
    print("SYNC OK")
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    logging.info(f"Zalogowano jako {client.user}")

# ========= KOMENDA =========
@tree.command(
    name="rollbackstworz",
    description="Tworzy prywatny kanał rollback",
    guild=discord.Object(id=GUILD_ID)
)
async def rollbackstworz(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔧 Rollback",
        description=(
            "**Na czym polega rollback?**\n"
            "Rollback służy do analizy gry i poprawy umiejętności.\n\n"
            "**Jak wysłać klipa?**\n"
            "Wrzuć pełne nagranie + timecodes z fightami."
        ),
        color=0x7B3FE4
    )

    await interaction.response.send_message(
        embed=embed,
        view=RollbackView()
    )

# ========= START =========
client.run(TOKEN)





