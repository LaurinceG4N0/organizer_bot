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
