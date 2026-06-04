import os
import sys
import logging
import asyncio
import discord
from discord import app_commands
from discord.ext import commands

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot.config import Config
from bot.database.db import init_db
from bot.commands.project import ProjectCommands
from bot.commands.plan import PlanCommands
from bot.commands.tasks import TaskCommands
from bot.commands.report import ReportCommands
from bot.commands.ping import PingCommands

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("organizer_bot")

# Discord intents
intents = discord.Intents.all()

class OrganizerBot(commands.Bot):
    async def setup_hook(self):
        """Load all cogs before bot connects."""
        logger.info("Loading cogs...")

        for CmdClass in [ProjectCommands, PlanCommands, TaskCommands, ReportCommands, PingCommands]:
            cog = CmdClass(self)
            await self.add_cog(cog)
            logger.info(f"  ✓ Loaded {CmdClass.__name__}")

        await asyncio.sleep(0.1)

bot = OrganizerBot(command_prefix="!", intents=intents)

# DB init
init_db()

# Test command - for debugging
@app_commands.command(name="ping", description="Test command")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    try:
        guild = discord.Object(id=int(Config.GUILD_ID)) if Config.GUILD_ID else None
        global_cmds = bot.tree._get_all_commands()
        logger.info(f"Global commands in tree: {len(global_cmds)}")
        if guild:
            guild_cmds = bot.tree._get_all_commands(guild=guild)
            logger.info(f"Guild commands in tree: {len(guild_cmds)}")
        
        if Config.GUILD_ID:
            logger.info("Syncing commands to guild...")
            synced = await bot.tree.sync(guild=guild)
        else:
            logger.info("Syncing commands globally...")
            synced = await bot.tree.sync()
        
        logger.info(f"Synced {len(synced)} command(s)")
        for cmd in synced:
            logger.info(f"  ✓ /{cmd.name}")
            
    except Exception as e:
        logger.error("Failed to sync commands: %s", e, exc_info=True)
    
    logger.info("Bot is operational!")


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    logger.error("Unhandled command error: %s", error, exc_info=True)
    msg = "❌ Une erreur inattendue s'est produite."
    if interaction.response.is_done():
        await interaction.followup.send(msg)
    else:
        await interaction.response.send_message(msg)


if __name__ == "__main__":
    if not Config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN non défini dans .env — bot non démarré.")
        sys.exit(1)
    bot.run(Config.DISCORD_TOKEN, log_handler=None)
