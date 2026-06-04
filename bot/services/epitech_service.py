from datetime import datetime, timedelta

class EpitechService:
    def get_school_schedule(self, date):
        """Simulate school schedule. In real implementation, fetch from API."""
        # Simulate a typical day: classes from 8:30 to 12:30, then projects
        schedule = [
            {"start": "08:30", "end": "10:30", "type": "class", "subject": "Programming"},
            {"start": "10:45", "end": "12:30", "type": "class", "subject": "System Administration"}
        ]
        return schedule

    def get_upcoming_deadlines(self):
        """Simulate upcoming deadlines."""
        return [
            {"name": "Project 1", "deadline": (datetime.now() + timedelta(days=7)).isoformat()},
            {"name": "Exam", "deadline": (datetime.now() + timedelta(days=14)).isoformat()}
        ]