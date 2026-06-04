import logging
from sqlalchemy.orm import Session
from bot.services.ai_service import AIService
from bot.services.project_service import ProjectService
from bot.config import Config

logger = logging.getLogger(__name__)


class Planner:
    def __init__(self, db: Session):
        self.ai = AIService()
        self.ps = ProjectService(db)

    def generate_daily_plan(self, discord_id: str, display_name: str) -> dict:
        projects = self.ps.list_projects(discord_id)
        selected = projects[: Config.MAX_PROJECTS_PER_DAY]

        project_data = []
        for p in selected:
            pending_tasks = [
                {
                    "name": t.name,
                    "description": t.description,
                    "estimated_hours": t.estimated_hours,
                }
                for t in p.tasks
                if not t.completed
            ]
            project_data.append(
                {
                    "name": p.name,
                    "description": p.description,
                    "priority": p.priority,
                    "difficulty": p.difficulty,
                    "pending_tasks": pending_tasks,
                }
            )

        constraints = {
            "wake_up": Config.WAKE_UP_TIME,
            "school_start": Config.SCHOOL_START,
            "school_end": Config.SCHOOL_END,
            "lunch_time": Config.LUNCH_TIME,
            "sleep_hours_min": Config.SLEEP_HOURS_MIN,
            "sleep_hours_max": Config.SLEEP_HOURS_MAX,
            "max_deep_work_hours": Config.MAX_DEEP_WORK_HOURS,
            "max_projects_per_day": Config.MAX_PROJECTS_PER_DAY,
        }

        return self.ai.generate_daily_plan(project_data, constraints)
