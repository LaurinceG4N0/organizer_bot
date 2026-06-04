import discord
from discord import app_commands
from discord.ext import commands
from bot.services.project_service import ProjectService
from bot.database.db import get_db


class ProjectCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="project_add", description="Ajouter un nouveau projet")
    @app_commands.describe(
        name="Nom du projet",
        description="Description détaillée",
        start_date="Date de début (AAAA-MM-JJ)",
        end_date="Date de fin (AAAA-MM-JJ)",
        team_size="Nombre de personnes dans l'équipe",
        difficulty="Difficulté estimée (optionnel : easy/medium/hard)",
    )
    async def project_add(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str,
        start_date: str,
        end_date: str,
        team_size: int = 1,
        difficulty: str = None,
    ):
        await interaction.response.defer(thinking=True)
        db = next(get_db())
        service = ProjectService(db)
        try:
            project_data = {
                "name": name,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "team_size": team_size,
                "difficulty": difficulty,
            }
            project = service.add_project(
                str(interaction.user.id),
                interaction.user.display_name,
                project_data,
            )
            task_count = len(project.tasks)
            embed = discord.Embed(
                title="✅ Projet ajouté",
                description=f"**{project.name}** a été créé avec succès.",
                color=discord.Color.green(),
            )
            embed.add_field(name="Difficulté", value=project.difficulty.capitalize(), inline=True)
            embed.add_field(name="Tâches générées", value=str(task_count), inline=True)
            embed.add_field(name="Deadline", value=project.end_date.strftime("%d/%m/%Y"), inline=True)
            embed.set_footer(text=f"ID projet : {project.id}")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : {e}")

    @app_commands.command(name="project_list", description="Lister vos projets en cours (triés par priorité)")
    async def project_list(self, interaction: discord.Interaction):
        db = next(get_db())
        service = ProjectService(db)
        projects = service.list_projects(str(interaction.user.id))
        if not projects:
            await interaction.response.send_message("📋 Aucun projet en cours.")
            return
        embed = discord.Embed(title="📋 Vos projets", color=discord.Color.blurple())
        for p in projects:
            total = len(p.tasks)
            done = sum(1 for t in p.tasks if t.completed)
            progress = f"{done}/{total} tâches"
            embed.add_field(
                name=f"#{p.id} — {p.name}",
                value=(
                    f"Priorité : **{p.priority:.1f}** | Difficulté : {p.difficulty}\n"
                    f"Deadline : {p.end_date.strftime('%d/%m/%Y')} | {progress}"
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="project_delete", description="Supprimer un projet (et toutes ses tâches)")
    @app_commands.describe(project_id="ID du projet à supprimer")
    async def project_delete(self, interaction: discord.Interaction, project_id: int):
        db = next(get_db())
        service = ProjectService(db)
        try:
            name = service.delete_project(str(interaction.user.id), project_id)
            await interaction.response.send_message(f"🗑️ Projet **{name}** supprimé.")
        except PermissionError as e:
            await interaction.response.send_message(f"❌ {e}")
