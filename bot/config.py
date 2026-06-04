import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///organizer.db")
    GUILD_ID: str | None = os.getenv("GUILD_ID")

    # Planning constraints (can be overridden via env)
    WAKE_UP_TIME: str = os.getenv("WAKE_UP_TIME", "07:30")
    SCHOOL_START: str = os.getenv("SCHOOL_START", "08:30")
    SCHOOL_END: str = os.getenv("SCHOOL_END", "12:30")
    LUNCH_TIME: str = os.getenv("LUNCH_TIME", "13:00")
    SLEEP_HOURS_MIN: int = int(os.getenv("SLEEP_HOURS_MIN", "7"))
    SLEEP_HOURS_MAX: int = int(os.getenv("SLEEP_HOURS_MAX", "8"))
    MAX_DEEP_WORK_HOURS: int = int(os.getenv("MAX_DEEP_WORK_HOURS", "8"))
    MAX_PROJECTS_PER_DAY: int = int(os.getenv("MAX_PROJECTS_PER_DAY", "2"))

    @staticmethod
    def get_guild_ids() -> list[int] | None:
        """Get guild IDs for app commands context."""
        if Config.GUILD_ID:
            return [int(Config.GUILD_ID)]
        return None
