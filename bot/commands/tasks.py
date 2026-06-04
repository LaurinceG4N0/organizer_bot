import discord
from discord import app_commands
from discord.ext import commands
from bot.services.project_service import ProjectService
from bot.database.db import get_db


class TaskCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="task_list", description="Lister les tâches d'un projet")
    @app_commands.describe(project_id="ID du projet")
    async def task_list(self, interaction: discord.Interaction, project_id: int):
        db = next(get_db())
        service = ProjectService(db)
        try:
            tasks = service.list_tasks(str(interaction.user.id), project_id)
            if not tasks:
                await interaction.response.send_message("📝 Aucune tâche pour ce projet.")
                return
            embed = discord.Embed(title=f"📝 Tâches — Projet #{project_id}", color=discord.Color.gold())
            for t in tasks:
                status = "✅" if t.completed else "⬜"
                embed.add_field(
                    name=f"{status} #{t.id} — {t.name}",
                    value=f"{t.description or 'Pas de description'} | ⏱ {t.estimated_hours}h",
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)
        except PermissionError as e:
            await interaction.response.send_message(f"❌ {e}")

    @app_commands.command(name="task_add", description="Ajouter manuellement une tâche à un projet")
    @app_commands.describe(
        project_id="ID du projet",
        name="Nom de la tâche",
        description="Description",
        hours="Heures estimées",
    )
    async def task_add(
        self,
        interaction: discord.Interaction,
        project_id: int,
        name: str,
        description: str = "",
        hours: float = 1.0,
    ):
        db = next(get_db())
        service = ProjectService(db)
        try:
            task = service.add_task(str(interaction.user.id), project_id, name, description, hours)
            await interaction.response.send_message(
                f"✅ Tâche **{task.name}** (#{task.id}) ajoutée au projet #{project_id}."
            )
        except PermissionError as e:
            await interaction.response.send_message(f"❌ {e}")

    @app_commands.command(name="done", description="Marquer une tâche comme terminée")
    @app_commands.describe(task_id="ID de la tâche à terminer")
    async def done(self, interaction: discord.Interaction, task_id: int):
        db = next(get_db())
        service = ProjectService(db)
        try:
            task = service.complete_task(str(interaction.user.id), task_id)
            await interaction.response.send_message(f"✅ Tâche **{task.name}** marquée comme terminée !")
        except (ValueError, PermissionError) as e:
            await interaction.response.send_message(f"❌ {e}")
