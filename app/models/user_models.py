"""User and Tool model definitions with ToolAssignment support."""

from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    tools = relationship("Tool", back_populates="owner")
    assignments = relationship(
        "ToolAssignment", back_populates="user", cascade="all, delete-orphan")


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    billing_cycle = Column(String, nullable=False)  # 'monthly', 'yearly'
    renewal_date = Column(Date, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tools")

    assignments = relationship(
        "ToolAssignment", back_populates="tool", cascade="all, delete-orphan")
    last_used = Column(Date, nullable=True)
