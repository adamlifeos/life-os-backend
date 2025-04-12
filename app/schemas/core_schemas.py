from pydantic import BaseModel
from typing import Optional

class IdentityBase(BaseModel):
    name: str
    ai_coach_persona: Optional[str] = None

class IdentityCreate(IdentityBase):
    pass

class Identity(IdentityBase):
    id: int
    user_id: int
    level: int = 1
    exp: int = 0
    x: int = 0
    y: int = 0

    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    ai_coach_persona: Optional[str] = None

class SkillCreate(SkillBase):
    identity_id: int

class Skill(SkillBase):
    id: int
    identity_id: int
    level: int = 1
    exp: int = 0
    x: int = 0
    y: int = 0

    class Config:
        from_attributes = True

class HabitBase(BaseModel):
    name: str
    skill_id: Optional[int] = None
    exp_reward: int = 10
    chrono_reward: int = 1

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    user_id: int
    streak: int = 0
    x: int = 0
    y: int = 0

    class Config:
        from_attributes = True
