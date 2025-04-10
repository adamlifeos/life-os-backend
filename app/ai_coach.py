from sqlalchemy.orm import Session
from . import models


def get_user_context(db: Session, user: models.User, identity_id: int = None, skill_id: int = None):
    context = {
        "user_level": user.level,
        "user_exp": user.exp,
        "chrono_points": user.chrono_points,
        "pending_tasks": [],
        "recent_habits": [],
    }

    # Get pending tasks
    query = db.query(models.Task).filter(
        models.Task.user_id == user.id,
        models.Task.completed == False
    )
    if identity_id:
        query = query.filter(models.Task.identity_id == identity_id)
    if skill_id:
        query = query.filter(models.Task.skill_id == skill_id)
    context["pending_tasks"] = [task.title for task in query.all()]

    # Get recent habits and their streaks
    query = db.query(models.Habit).filter(models.Habit.user_id == user.id)
    if skill_id:
        query = query.filter(models.Habit.skill_id == skill_id)
    habits = query.all()
    context["recent_habits"] = [
        {"name": habit.name, "streak": habit.streak}
        for habit in habits
    ]

    return context


def get_ai_coach_response(user_input: str, persona: str, context: dict) -> str:
    import os
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    print("🔑 Using API Key:", api_key[:10])  # DEBUGGING LINE

    if not api_key or "sk-" not in api_key:
        raise ValueError("❌ OPENAI_API_KEY not found or invalid in environment variables")

    client = OpenAI(api_key=api_key)

    prompt = f"""You are an AI coach with the following persona: {persona}

User Context:
- Level: {context['user_level']}
- Experience Points: {context['user_exp']}
- Chrono Points: {context['chrono_points']}
- Pending Tasks: {', '.join(context['pending_tasks']) if context['pending_tasks'] else 'None'}
- Active Habits: {', '.join(f"{h['name']} (streak: {h['streak']})" for h in context['recent_habits']) if context['recent_habits'] else 'None'}

User Input: {user_input}

Please provide motivational guidance and practical advice while staying in character as the specified persona."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=500,
        temperature=0.7
    )

    return response.choices[0].message.content