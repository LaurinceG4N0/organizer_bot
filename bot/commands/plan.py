import discord
from discord import app_commands
from discord.ext import commands
from bot.services.planner import Planner
from bot.services.scheduler import Scheduler
from bot.database.db import get_db


class PlanCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="plan", description="Générer le plan optimisé de la journée")
    async def plan(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        db = next(get_db())
        planner = Planner(db)
        scheduler = Scheduler(db)
        try:
            daily_plan = planner.generate_daily_plan(
                str(interaction.user.id), interaction.user.display_name
            )
            scheduler.save_plan(str(interaction.user.id), daily_plan)

            embed = discord.Embed(
                title="📅 Plan de la journée",
                color=discord.Color.teal(),
            )
            embed.add_field(
                name="🌅 Réveil / 🌙 Coucher",
                value=f"{daily_plan.get('wake_up', '?')} → {daily_plan.get('sleep', '?')}",
                inline=False,
            )

            TYPE_EMOJI = {
                "school": "🏫",
                "work": "💻",
                "lunch": "🍽️",
                "break": "☕",
                "personal": "🏃",
            }
            lines = []
            for slot in daily_plan.get("day_plan", []):
                emoji = TYPE_EMOJI.get(slot.get("type", ""), "📌")
                line = f"`{slot['start']}–{slot['end']}` {emoji} **{slot.get('type', '').capitalize()}**"
                if "project" in slot and "task" in slot:
                    line += f" — {slot['project']} : _{slot['task']}_"
                lines.append(line)

            embed.add_field(name="Programme", value="\n".join(lines) or "Aucun créneau", inline=False)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la génération du plan : {e}")
