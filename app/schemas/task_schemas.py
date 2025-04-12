from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    title: str
    skill_id: Optional[int] = None
    identity_id: Optional[int] = None
    exp_reward: int = 10
    chrono_reward: int = 1

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    user_id: int
    completed: bool = False

    class Config:
        from_attributes = True

class RewardBase(BaseModel):
    name: str
    cost: int

class RewardCreate(RewardBase):
    pass

class Reward(RewardBase):
    id: int
    user_id: int
    redeemed: bool = False

    class Config:
        from_attributes = True
