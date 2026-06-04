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
