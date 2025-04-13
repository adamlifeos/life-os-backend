from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, auth, ai_coach
from .schemas import auth_schemas, core_schemas, task_schemas, ai_coach_schemas
from .routers import items
from .database import engine, get_db
from .config import settings
import logging
import re

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life OS API")

# Configure CORS *before* including routers
NETLIFY_MAIN = "https://life-os.netlify.app"
NETLIFY_PREVIEW_REGEX = r"https:\/\/[a-z0-9-]+--life-os\.netlify\.app"  # Regex for previews
LOCAL_DEV = "http://localhost:3000"
LOCAL_DEV_ALT = "http://127.0.0.1:3000"
WINDSURF_DEV_PLACEHOLDER = "https://placeholder-username-93068.windsurf.build"
WINDSURF_DEV_ACTUAL = "https://life-os-frontend-windsurf.build"

# Combine all allowed origins
allowed_origins_list = [
    LOCAL_DEV,
    LOCAL_DEV_ALT,
    WINDSURF_DEV_PLACEHOLDER,
    WINDSURF_DEV_ACTUAL,
    NETLIFY_MAIN,
    "https://placeholder-username-93068.windsurf.build",  # Current deployment URL
    "https://life-os.netlify.app",  # Netlify production URL
    "https://life-os-frontend-windsurf.build",  # Windsurf production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_origin_regex=NETLIFY_PREVIEW_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers *after* adding middleware
app.include_router(items.router)

# Auth endpoints
@app.post("/token", response_model=auth_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# -- Temporary alias for /auth/login to help frontend CORS troubleshooting
logger = logging.getLogger('cors_debug')

@app.options('/auth/login')
async def auth_login_options(request: Request):
    # Debug logger: log all pertinent info for CORS preflight
    logger.info("CORS preflight OPTIONS for /auth/login - Origin: %s, Path: %s, Method: %s, Headers: %s",
                request.headers.get('origin'), request.url.path, request.method, dict(request.headers))
    return Response(status_code=200)

@app.post('/auth/login')
async def auth_login_alias(request: Request):
    # Temporary alias route that forwards to the existing /token handler
    # Assumes the /token endpoint function is named 'login_for_access_token'.
    return await login_for_access_token(request)

# User endpoints
@app.post("/users/", response_model=auth_schemas.User)
def create_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | 
        (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=auth_schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

# Add cascading delete for identities
def delete_identity_cascade(db: Session, identity_id: int):
    # Delete linked skills first
    skills = db.query(models.Skill).filter(models.Skill.identity_id == identity_id).all()
    for skill in skills:
        delete_skill_cascade(db, skill.id)
    
    # Delete linked tasks
    db.query(models.Task).filter(models.Task.identity_id == identity_id).delete()
    
    # Delete the identity
    db.query(models.Identity).filter(models.Identity.id == identity_id).delete()

# Add cascading delete for skills
def delete_skill_cascade(db: Session, skill_id: int):
    # Delete linked habits
    db.query(models.Habit).filter(models.Habit.skill_id == skill_id).delete()
    
    # Delete linked tasks
    db.query(models.Task).filter(models.Task.skill_id == skill_id).delete()
    
    # Delete the skill
    db.query(models.Skill).filter(models.Skill.id == skill_id).delete()

# Identity endpoints
@app.post("/identities/", response_model=core_schemas.Identity)
def create_identity(
    identity: core_schemas.IdentityCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_identity = models.Identity(**identity.model_dump(), user_id=current_user.id)
    db.add(db_identity)
    db.commit()
    db.refresh(db_identity)
    return db_identity

@app.get("/identities/", response_model=List[core_schemas.Identity])
def read_identities(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Identity).filter(models.Identity.user_id == current_user.id).all()

# Skill endpoints
@app.post("/skills/", response_model=core_schemas.Skill)
def create_skill(
    skill: core_schemas.SkillCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    identity = db.query(models.Identity).filter(
        models.Identity.id == skill.identity_id,
        models.Identity.user_id == current_user.id
    ).first()
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    
    db_skill = models.Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@app.get("/skills/", response_model=List[core_schemas.Skill])
def read_skills(
    identity_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Skill).filter(models.Skill.identity_id == identity_id).all()

# Habit endpoints
@app.post("/habits/", response_model=core_schemas.Habit)
def create_habit(
    habit: core_schemas.HabitCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if habit.skill_id:
        skill = db.query(models.Skill).filter(models.Skill.id == habit.skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
    
    db_habit = models.Habit(**habit.model_dump(), user_id=current_user.id)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@app.post("/habits/{habit_id}/complete")
def complete_habit(
    habit_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    habit = db.query(models.Habit).filter(
        models.Habit.id == habit_id,
        models.Habit.user_id == current_user.id
    ).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Update streak and last_completed
    if habit.last_completed:
        time_since_last = datetime.utcnow() - habit.last_completed
        if time_since_last.days > 1:
            habit.streak = 1
        else:
            habit.streak += 1
    else:
        habit.streak = 1
    habit.last_completed = datetime.utcnow()

    # Award rewards
    current_user.exp += habit.exp_reward
    current_user.chrono_points += habit.chrono_reward

    # Update skill exp if applicable
    if habit.skill_id:
        skill = db.query(models.Skill).filter(models.Skill.id == habit.skill_id).first()
        if skill:
            skill.exp += habit.exp_reward

    db.commit()
    return {"status": "success", "streak": habit.streak}

# Task endpoints
@app.post("/tasks/", response_model=task_schemas.Task)
def create_task(
    task: task_schemas.TaskCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_task = models.Task(**task.model_dump(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.completed:
        task.completed = True
        current_user.exp += task.exp_reward
        current_user.chrono_points += task.chrono_reward

        # Update skill exp if applicable
        if task.skill_id:
            skill = db.query(models.Skill).filter(models.Skill.id == task.skill_id).first()
            if skill:
                skill.exp += task.exp_reward

        # Update identity exp if applicable
        if task.identity_id:
            identity = db.query(models.Identity).filter(models.Identity.id == task.identity_id).first()
            if identity:
                identity.exp += task.exp_reward

        db.commit()
    return {"status": "success"}

# Level up endpoints
@app.post("/identities/{identity_id}/level-up")
def level_up_identity(
    identity_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    identity = db.query(models.Identity).filter(
        models.Identity.id == identity_id,
        models.Identity.user_id == current_user.id
    ).first()
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    levels_gained = 0
    while identity.exp >= 100:
        identity.level += 1
        identity.exp -= 100
        levels_gained += 1

    if levels_gained > 0:
        db.commit()
        return {"status": "success", "levels_gained": levels_gained, "new_level": identity.level}
    return {"status": "no_change"}

@app.post("/skills/{skill_id}/level-up")
def level_up_skill(
    skill_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(models.Skill).join(models.Identity).filter(
        models.Skill.id == skill_id,
        models.Identity.user_id == current_user.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    levels_gained = 0
    while skill.exp >= 100:
        skill.level += 1
        skill.exp -= 100
        levels_gained += 1

    if levels_gained > 0:
        db.commit()
        return {"status": "success", "levels_gained": levels_gained, "new_level": skill.level}
    return {"status": "no_change"}

# AI Coach endpoints
@app.post("/identities/{identity_id}/ai-coach")
async def get_identity_ai_coach(
    identity_id: int,
    request: ai_coach_schemas.AICoachRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    identity = db.query(models.Identity).filter(
        models.Identity.id == identity_id,
        models.Identity.user_id == current_user.id
    ).first()
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")

    context = ai_coach.get_user_context(db, current_user, identity_id=identity_id)
    response = ai_coach.get_ai_coach_response(
        request.user_input,
        identity.ai_coach_persona,
        context
    )
    return {"response": response}

@app.post("/skills/{skill_id}/ai-coach")
async def get_skill_ai_coach(
    skill_id: int,
    request: ai_coach_schemas.AICoachRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    skill = db.query(models.Skill).join(models.Identity).filter(
        models.Skill.id == skill_id,
        models.Identity.user_id == current_user.id
    ).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    context = ai_coach.get_user_context(db, current_user, skill_id=skill_id)
    response = ai_coach.get_ai_coach_response(
        request.user_input,
        skill.ai_coach_persona,
        context
    )
    return {"response": response}
