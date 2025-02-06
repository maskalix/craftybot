import os
import requests
import logging
import discord
from discord.ext import commands
from discord import app_commands

# ---------------------------------
# ---- Configuration --------------
# ---------------------------------
CRAFTY_API_BASE_URL = os.getenv("CRAFTY_API_BASE_URL")
CRAFTY_USERNAME = os.getenv("CRAFTY_USERNAME")
CRAFTY_PASSWORD = os.getenv("CRAFTY_PASSWORD")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CRAFTY_SERVER_ID = os.getenv("CRAFTY_SERVER_ID")
CRAFTY_SERVER_URL = os.getenv("CRAFTY_SERVER_URL")
CRAFTY_SERVER_TYPE = os.getenv("CRAFTY_SERVER_ID")

if not all([BOT_TOKEN, CRAFTY_API_BASE_URL, CRAFTY_USERNAME, CRAFTY_PASSWORD, CRAFTY_SERVER_ID]):
    raise ValueError("❌ Missing environment variables. Please check your .env file.")

# ---------------------------------
# ---- Logging Setup --------------
# ---------------------------------
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)

# ---------------------------------
# ---- Discord Bot Setup ----------
# ---------------------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------------------------
# ---- Global Variable for Token ---
# ---------------------------------
CRAFTY_API_TOKEN = None

# ---------------------------------
# ---- Authentication Function ----
# ---------------------------------
def login_to_crafty():
    """Logs in to Crafty Controller v2 and retrieves an API token."""
    global CRAFTY_API_TOKEN
    url = f"{CRAFTY_API_BASE_URL}/api/v2/auth/login"
    data = {"username": CRAFTY_USERNAME, "password": CRAFTY_PASSWORD}

    try:
        response = requests.post(url, json=data, verify=False)
        response.raise_for_status()
        token_data = response.json()
        
        if token_data.get("status") == "ok" and "data" in token_data and "token" in token_data["data"]:
            CRAFTY_API_TOKEN = token_data["data"]["token"]
            logging.info("✅ Successfully logged in to Crafty Controller and retrieved API token.")
        else:
            logging.error(f"❌ Failed to retrieve API token. Response: {token_data}")
            CRAFTY_API_TOKEN = None

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Crafty Controller login failed: {e}")
        CRAFTY_API_TOKEN = None

# ---------------------------------
# ---- Utility Functions ----------
# ---------------------------------
def send_crafty_command(action):
    """
    Sends a start/stop/restart command to the Crafty Controller API.
    """
    global CRAFTY_API_TOKEN

    if not CRAFTY_API_TOKEN:
        login_to_crafty()

    url = f"{CRAFTY_API_BASE_URL}/api/v2/servers/{CRAFTY_SERVER_ID}/action/{action}"
    headers = {"Authorization": f"Bearer {CRAFTY_API_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, timeout=30, verify=False)

        if response.status_code == 401:
            logging.warning("⚠️ Token expired! Logging in again.")
            login_to_crafty()
            headers["Authorization"] = f"Bearer {CRAFTY_API_TOKEN}"
            response = requests.post(url, headers=headers, timeout=30, verify=False)

        response.raise_for_status()
        return True, f"✅ {action.replace('_', ' ').capitalize()} command sent successfully!"

    except requests.exceptions.RequestException as e:
        return False, f"❌ Error sending {action} command: {e}"

def get_server_info():
    """Fetches server info from Crafty API."""
    global CRAFTY_API_TOKEN

    if not CRAFTY_API_TOKEN:
        login_to_crafty()

    url = f"{CRAFTY_API_BASE_URL}/api/v2/servers/{CRAFTY_SERVER_ID}"
    headers = {"Authorization": f"Bearer {CRAFTY_API_TOKEN}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)

        if response.status_code == 401:
            logging.warning("⚠️ Token expired! Logging in again.")
            login_to_crafty()
            headers["Authorization"] = f"Bearer {CRAFTY_API_TOKEN}"
            response = requests.get(url, headers=headers, timeout=30, verify=False)

        response.raise_for_status()

        server_data = response.json()
        logging.info(f"📡 Crafty API Response: {server_data}")
        return server_data

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Failed to connect to Crafty Controller: {e}")
        return None

# ---------------------------------
# ---- Discord UI (Buttons) -------
# ---------------------------------
class ServerControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = send_crafty_command("start_server")
        await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = send_crafty_command("stop_server")
        await interaction.response.send_message(message, ephemeral=True)

    @discord.ui.button(label="Restart", style=discord.ButtonStyle.primary)
    async def restart_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success, message = send_crafty_command("restart_server")
        await interaction.response.send_message(message, ephemeral=True)

# ---------------------------------
# ---- Slash Command --------------
# ---------------------------------
@tree.command(name="serverinfo", description="Show server info and control buttons.")
async def serverinfo(interaction: discord.Interaction):
    """
    Slash command to get server info from Crafty and display control buttons.
    """
    data = get_server_info()
    if not data or "data" not in data:
        await interaction.response.send_message("❌ Failed to fetch server info from Crafty.", ephemeral=True)
        return

    server_data = data["data"]

    # Extract values
    server_name = server_data.get("server_name", "Unknown Server")
    server_type = CRAFTY_SERVER_TYPE
    server_ip = CRAFTY_SERVER_URL

    # Extract version from executable
    executable = server_data.get("executable", "Unknown")
    version = executable.split("-")[-1].replace(".jar", "") if "-" in executable else "Unknown"

    embed = discord.Embed(title=f"{server_name}", color=discord.Color.green())
    embed.add_field(name="IP Address", value=server_ip, inline=False)
    embed.add_field(name="Type", value=server_type, inline=False)
    embed.add_field(name="Version", value=version, inline=False)
    embed.set_footer(text="Powered by Crafty Controller")

    view = ServerControlView()
    await interaction.response.send_message(embed=embed, view=view)

# ---------------------------------
# ---- Bot Startup ----------------
# ---------------------------------
@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    login_to_crafty()

    try:
        synced = await tree.sync()
        logging.info(f"✅ Slash commands synced: {len(synced)} commands")
    except Exception as e:
        logging.error(f"❌ Error syncing slash commands: {e}")

def main():
    logging.info("🚀 Starting Discord bot...")
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    main()
