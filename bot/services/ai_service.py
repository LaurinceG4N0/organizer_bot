import json
import logging
from openai import OpenAI
from bot.config import Config

logger = logging.getLogger(__name__)
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=Config.OPENAI_API_KEY)
    return _client


def _chat(prompt: str, max_tokens: int = 1500) -> dict:
    """Call OpenAI and return parsed JSON. Raises on failure."""
    response = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw)


class AIService:
    def analyze_project(self, project_data: dict) -> dict:
        """
        Returns:
        {
          "estimated_difficulty": "easy|medium|hard",
          "tasks": [{"name": str, "description": str, "estimated_hours": float}]
        }
        """
        prompt = f"""
You are a project manager assistant. Analyze the following project and break it
into actionable tasks for a student developer.

Project name: {project_data['name']}
Description:  {project_data['description']}
Start date:   {project_data['start_date']}
End date:     {project_data['end_date']}
Team size:    {project_data['team_size']}
Difficulty:   {project_data.get('difficulty', 'unknown')}

Return a JSON object with exactly these keys:
- "estimated_difficulty": one of "easy", "medium", "hard"
- "tasks": an array of objects, each with:
    "name" (string), "description" (string), "estimated_hours" (float)

Keep tasks concrete and realistic. Maximum 10 tasks.
"""
        result = _chat(prompt)
        logger.debug("analyze_project result: %s", result)
        return result

    def generate_daily_plan(self, projects: list, constraints: dict) -> dict:
        """
        Returns:
        {
          "wake_up": "HH:MM",
          "sleep": "HH:MM",
          "day_plan": [{"start": "HH:MM", "end": "HH:MM", "type": str, "project"?: str, "task"?: str}]
        }
        """
        prompt = f"""
You are a scheduling assistant for an engineering student.
Build a realistic daily schedule using the constraints and projects below.

Constraints:
- Wake up: {constraints['wake_up']}
- School: {constraints['school_start']} → {constraints['school_end']}
- Lunch break: {constraints['lunch_time']} (30 min)
- Minimum sleep: {constraints['sleep_hours_min']}h, maximum: {constraints['sleep_hours_max']}h
- Maximum deep work: {constraints['max_deep_work_hours']}h per day
- Maximum projects per day: {constraints['max_projects_per_day']}

Projects to schedule (ordered by priority):
{json.dumps(projects, ensure_ascii=False, indent=2)}

Rules:
1. Include school, lunch, breaks, and personal time.
2. Assign specific pending tasks to work slots.
3. Do not exceed max deep work or max projects limits.
4. End time must allow minimum sleep.

Return a JSON object with exactly these keys:
- "wake_up": "HH:MM"
- "sleep":   "HH:MM"
- "day_plan": array of {{"start":"HH:MM","end":"HH:MM","type":"school|work|lunch|break|personal","project":"...","task":"..."}}
  (omit "project" and "task" keys for non-work slots)
"""
        result = _chat(prompt, max_tokens=2000)
        logger.debug("generate_daily_plan result: %s", result)
        return result
