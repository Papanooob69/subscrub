from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ToolAssignment(Base):
    __tablename__ = "tool_assignments"
    __table_args__ = (
        UniqueConstraint("tool_id", "user_id", name="uq_tool_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(Integer, ForeignKey(
        "tools.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    tool = relationship("Tool", back_populates="assignments")
    user = relationship("User", back_populates="assignments")
