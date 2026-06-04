import discord
from discord import app_commands
from discord.ext import commands
from bot.services.scheduler import Scheduler
from bot.services.project_service import ProjectService
from bot.database.db import get_db


class ReportCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="report", description="Rapport de progression hebdomadaire")
    async def report(self, interaction: discord.Interaction):
        db = next(get_db())
        scheduler = Scheduler(db)
        ps = ProjectService(db)

        history = scheduler.get_history(str(interaction.user.id), 7)
        projects = ps.list_projects(str(interaction.user.id))

        total_tasks = sum(len(p.tasks) for p in projects)
        done_tasks = sum(sum(1 for t in p.tasks if t.completed) for p in projects)
        completion_pct = round(done_tasks / total_tasks * 100) if total_tasks else 0

        embed = discord.Embed(
            title="📊 Rapport hebdomadaire",
            color=discord.Color.orange(),
        )
        embed.add_field(name="Plans générés (7j)", value=str(len(history)), inline=True)
        embed.add_field(name="Tâches complétées", value=f"{done_tasks}/{total_tasks} ({completion_pct}%)", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)

        if projects:
            proj_lines = []
            for p in projects:
                done = sum(1 for t in p.tasks if t.completed)
                total = len(p.tasks)
                bar_filled = int((done / total * 10)) if total else 0
                bar = "█" * bar_filled + "░" * (10 - bar_filled)
                proj_lines.append(f"**{p.name}** [{bar}] {done}/{total}")
            embed.add_field(name="Projets", value="\n".join(proj_lines), inline=False)

        await interaction.response.send_message(embed=embed)
