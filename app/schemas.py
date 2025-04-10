from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# Base schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class IdentityBase(BaseModel):
    name: str
    ai_coach_persona: str

class SkillBase(BaseModel):
    name: str
    ai_coach_persona: str

class HabitBase(BaseModel):
    name: str
    exp_reward: int = 10
    chrono_reward: int = 1
    skill_id: Optional[int] = None

class TaskBase(BaseModel):
    title: str
    exp_reward: int = 10
    chrono_reward: int = 1
    skill_id: Optional[int] = None
    identity_id: Optional[int] = None

class RewardBase(BaseModel):
    name: str
    cost: int

# Create schemas
class UserCreate(UserBase):
    password: str

class IdentityCreate(IdentityBase):
    pass

class SkillCreate(SkillBase):
    identity_id: int

class HabitCreate(HabitBase):
    pass

class TaskCreate(TaskBase):
    pass

class RewardCreate(RewardBase):
    pass

# Response schemas
class User(UserBase):
    id: int
    chrono_points: int
    exp: int
    level: int
    created_at: datetime

    class Config:
        from_attributes = True

class Identity(IdentityBase):
    id: int
    user_id: int
    level: int
    exp: int
    created_at: datetime

    class Config:
        from_attributes = True

class Skill(SkillBase):
    id: int
    identity_id: int
    level: int
    exp: int
    created_at: datetime

    class Config:
        from_attributes = True

class Habit(HabitBase):
    id: int
    user_id: int
    streak: int
    last_completed: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class Task(TaskBase):
    id: int
    user_id: int
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Reward(RewardBase):
    id: int
    user_id: int
    redeemed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# AI Coach schemas
class AICoachRequest(BaseModel):
    user_input: str
