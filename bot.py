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

# ========= RENDER / PORT =========
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ========= USTAWIENIA =========
GUILD_ID = 1410955423648845825  # <-- ID SERWERA
CATEGORY_NAME = "Rollbacks"

# ========= VIEW =========
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

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if not category:
            await interaction.response.send_message(
                "❌ Brak kategorii **Rollbacks**",
                ephemeral=True
            )
            return

        channel_name = f"rollback-{member.name}".lower()

        if discord.utils.get(category.text_channels, name=channel_name):
            await interaction.response.send_message(
                "❌ Masz już otwarty rollback",
                ephemeral=True
            )
            return

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
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(
            f"✅ Utworzono {channel.mention}",
            ephemeral=True
        )

# ========= READY =========
@client.event
async def on_ready():
    print("SYNC OK")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
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
            "Kanał służy do analizy gry i poprawy umiejętności.\n\n"
            "**Jak wysłać klipa?**\n"
            "Pełne nagranie + timecodes."
        ),
        color=0x7B3FE4
    )

    await interaction.response.send_message(
        embed=embed,
        view=RollbackView()
    )

# ========= START =========
client.run(TOKEN)







