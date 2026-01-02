import discord
from discord import app_commands
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

# ===== INTENTS (KLUCZOWE) =====
intents = discord.Intents.default()
intents.guilds = True  # <<< BEZ TEGO SLASH NIE DZIAŁAJĄ

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ===== FLASK (PORT DLA RENDER) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot działa"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# ===== READY =====
GUILD_ID = 1410955423648845825  # <<< TWOJE ID SERWERA

@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    logging.info(f"Zalogowano jako {client.user}")

# ===== KOMENDA =====
@tree.command(
    name="rollbackstworz",
    description="Tworzy kanał rollback i wysyła instrukcję",
    guild=discord.Object(id=GUILD_ID)
)
async def rollbackstworz(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔧 Rollback",
        description=(
            "**Na czym i co ma na celu stworzenie rollbacka?**\n"
            "Tworzycie rollbacka tylko z myślą o to, żeby polepszyć swoje "
            "umiejętności gry, razem z zarządem będziemy dokładnie analizować "
            "wysyłane przez was klipy i podpowiadać wam co mogliście zrobić "
            "lepiej aby jak najszybciej progresować.\n\n"
            "**Jak macie wysłać poprawnie klipa?**\n"
            "Aby poprawnie wysłać klipa musicie wstawić całe nagranie "
            "z np. MCL na swój stworzony kanał wraz "
            "z rozpisanymi timecodes."
        ),
        color=0x7B3FE4
    )

    await interaction.response.send_message(embed=embed)

# ===== START =====
client.run(TOKEN)



