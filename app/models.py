from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    chrono_points = Column(Integer, default=0)
    exp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    identities = relationship("Identity", back_populates="user")
    habits = relationship("Habit", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    rewards = relationship("Reward", back_populates="user")

class Identity(Base):
    __tablename__ = "identities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    ai_coach_persona = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="identities")
    skills = relationship("Skill", back_populates="identity")
    tasks = relationship("Task", back_populates="identity")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"))
    name = Column(String)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    ai_coach_persona = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    identity = relationship("Identity", back_populates="skills")
    habits = relationship("Habit", back_populates="skill")
    tasks = relationship("Task", back_populates="skill")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    name = Column(String)
    streak = Column(Integer, default=0)
    last_completed = Column(DateTime, nullable=True)
    exp_reward = Column(Integer, default=10)
    chrono_reward = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="habits")
    skill = relationship("Skill", back_populates="habits")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=True)
    title = Column(String)
    completed = Column(Boolean, default=False)
    exp_reward = Column(Integer, default=10)
    chrono_reward = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    skill = relationship("Skill", back_populates="tasks")
    identity = relationship("Identity", back_populates="tasks")

class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    cost = Column(Integer)
    redeemed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rewards")
