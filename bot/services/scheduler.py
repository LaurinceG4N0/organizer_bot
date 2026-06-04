import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from bot.database.models import ScheduleHistory, User

logger = logging.getLogger(__name__)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Scheduler:
    def __init__(self, db: Session):
        self.db = db

    def save_plan(self, discord_id: str, plan: dict):
        user = self.db.query(User).filter(User.discord_id == str(discord_id)).first()
        if not user:
            return
        entry = ScheduleHistory(user_id=user.id, date=_utcnow(), plan=json.dumps(plan, ensure_ascii=False))
        self.db.add(entry)
        self.db.commit()
        logger.info("Saved plan for user %s", discord_id)

    def get_history(self, discord_id: str, limit: int = 7) -> list[ScheduleHistory]:
        user = self.db.query(User).filter(User.discord_id == str(discord_id)).first()
        if not user:
            return []
        return (
            self.db.query(ScheduleHistory)
            .filter(ScheduleHistory.user_id == user.id)
            .order_by(ScheduleHistory.date.desc())
            .limit(limit)
            .all()
        )
