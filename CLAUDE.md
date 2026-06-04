# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtualenv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python3 bot/main.py
```

There are no tests or linter configured. The bot logs to both stdout and `bot.log`.

## Environment

Required `.env` variables:
- `DISCORD_TOKEN` — bot token from Discord Developer Portal
- `OPENAI_API_KEY` — key for GPT-4o-mini calls
- `GUILD_ID` — (optional) restrict slash command sync to one guild (faster for dev)
- `DATABASE_URL` — defaults to `sqlite:///organizer.db`

Planning constraints (`WAKE_UP_TIME`, `SCHOOL_START`, `SCHOOL_END`, `LUNCH_TIME`, `SLEEP_HOURS_MIN`, `SLEEP_HOURS_MAX`, `MAX_DEEP_WORK_HOURS`, `MAX_PROJECTS_PER_DAY`) are all overridable via `.env`.

## Architecture

### Entry point & bot setup (`bot/main.py`)
`OrganizerBot` subclasses `commands.Bot`. All slash command cogs are loaded in `setup_hook`. Command sync happens in `on_ready` — guild-scoped if `GUILD_ID` is set, global otherwise. Each cog class is in `bot/commands/`.

### Data layer (`bot/database/`)
SQLAlchemy ORM with SQLite (default). Four models: `User`, `Project`, `Task`, `ScheduleHistory`. Users are auto-created on first interaction via `ProjectService.get_or_create_user`. Cascade deletes are set on all foreign keys. Priority is a computed float stored on `Project`, recalculated on every `list_projects` call via `_refresh_priority` (formula: `urgency = 10 - days_left` + difficulty score 1/2/3).

### Service layer (`bot/services/`)
- **`ProjectService`** — all CRUD for projects and tasks. Owns the ownership-enforcement pattern (`_owned_project`): every mutating method looks up the user by `discord_id` and verifies the project belongs to them before acting.
- **`AIService`** — thin wrapper around OpenAI. Two calls: `analyze_project` (returns difficulty + task list as JSON) and `generate_daily_plan` (returns a timed day schedule as JSON). Both use `response_format={"type": "json_object"}` for reliable parsing.
- **`Planner`** — orchestrates daily plan generation: fetches the user's top-priority projects, extracts their pending tasks, builds a constraints dict from `Config`, then delegates to `AIService.generate_daily_plan`.
- **`scheduler.py`** — stores plan history in `ScheduleHistory`. (APScheduler is in `requirements.txt` but the daily 7h00 auto-send is not yet wired up.)

### Command layer (`bot/commands/`)
Each file is a `commands.Cog`. Commands receive a `discord.Interaction`, open a DB session, instantiate the relevant service, and format the result as an embed. The session is always passed explicitly — there is no global session or dependency injection framework.

### Multi-user isolation
Users are identified by `interaction.user.id` (Discord snowflake stored as string). `ProjectService._owned_project` enforces that every project/task operation is scoped to the calling user. The AI prompts do not receive any cross-user data.
