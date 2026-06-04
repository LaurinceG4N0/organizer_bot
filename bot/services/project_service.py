import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from bot.database.models import User, Project, Task
from bot.services.ai_service import AIService

logger = logging.getLogger(__name__)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    # ── user helpers ──────────────────────────────────────────────────────────

    def get_or_create_user(self, discord_id: str, name: str) -> User:
        user = self.db.query(User).filter(User.discord_id == str(discord_id)).first()
        if not user:
            user = User(discord_id=str(discord_id), name=name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info("Created user %s (%s)", name, discord_id)
        return user

    # ── projects ──────────────────────────────────────────────────────────────

    def add_project(self, discord_id: str, name: str, project_data: dict) -> Project:
        user = self.get_or_create_user(discord_id, name)

        # AI analysis to get difficulty + tasks
        analysis = self.ai.analyze_project(project_data)
        difficulty = analysis.get("estimated_difficulty", project_data.get("difficulty", "medium"))
        tasks_data = analysis.get("tasks", [])

        project = Project(
            user_id=user.id,
            name=project_data["name"],
            description=project_data["description"],
            start_date=datetime.fromisoformat(project_data["start_date"]),
            end_date=datetime.fromisoformat(project_data["end_date"]),
            team_size=project_data.get("team_size", 1),
            difficulty=difficulty,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        for t in tasks_data:
            task = Task(
                project_id=project.id,
                name=t["name"],
                description=t.get("description", ""),
                estimated_hours=float(t.get("estimated_hours", 1)),
            )
            self.db.add(task)
        self.db.commit()
        self._refresh_priority(project)
        return project

    def add_task(self, discord_id: str, project_id: int, name: str, description: str, hours: float) -> Task:
        project = self._owned_project(discord_id, project_id)
        task = Task(project_id=project.id, name=name, description=description, estimated_hours=hours)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_project(self, discord_id: str, project_id: int) -> str:
        project = self._owned_project(discord_id, project_id)
        name = project.name
        self.db.delete(project)
        self.db.commit()
        return name

    def list_projects(self, discord_id: str) -> list[Project]:
        user = self.db.query(User).filter(User.discord_id == str(discord_id)).first()
        if not user:
            return []
        projects = (
            self.db.query(Project)
            .filter(Project.user_id == user.id, Project.is_archived == False)
            .all()
        )
        for p in projects:
            self._refresh_priority(p)
        return sorted(projects, key=lambda x: x.priority, reverse=True)

    def list_tasks(self, discord_id: str, project_id: int) -> list[Task]:
        project = self._owned_project(discord_id, project_id)
        return project.tasks

    def complete_task(self, discord_id: str, task_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError("Task not found.")
        project = self._owned_project(discord_id, task.project_id)  # security check
        task.completed = True
        task.completed_at = _utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    # ── private ───────────────────────────────────────────────────────────────

    def _owned_project(self, discord_id: str, project_id: int) -> Project:
        user = self.db.query(User).filter(User.discord_id == str(discord_id)).first()
        if not user:
            raise PermissionError("User not found.")
        project = self.db.query(Project).filter(
            Project.id == project_id, Project.user_id == user.id
        ).first()
        if not project:
            raise PermissionError("Project not found or access denied.")
        return project

    def _refresh_priority(self, project: Project):
        days_left = max(0, (project.end_date - _utcnow()).days)
        urgency = max(0, 10 - days_left)
        diff_score = {"easy": 1, "medium": 2, "hard": 3}.get(project.difficulty or "medium", 2)
        project.priority = urgency + diff_score
        self.db.commit()
