from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from datetime import date, timedelta
from app.database import get_db
from app.models.user_models import User, Tool
from app.models.tool_assignment import ToolAssignment

from app.schemas.auth_schemas import UserRead
from app.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("/inactive", response_model=list[UserRead])
def get_inactive_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thirty_days_ago = date.today() - timedelta(days=30)

    # Explicitly create a select() for Tool IDs
    tools_owned_stmt = select(Tool.id).where(Tool.owner_id == current_user.id)

    # Filter assignments for those tools (no SAWarning now)
    assignments = db.query(ToolAssignment).options(
        joinedload(ToolAssignment.user)
    ).filter(ToolAssignment.tool_id.in_(tools_owned_stmt)).all()

    # Track latest usage per user
    user_usage = {}

    for assignment in assignments:
        user = assignment.user
        last_used = assignment.last_used_at

        if user.id not in user_usage:
            user_usage[user.id] = {
                "user": user,
                "most_recent_use": last_used
            }
        else:
            existing = user_usage[user.id]["most_recent_use"]
            if last_used and (not existing or last_used > existing):
                user_usage[user.id]["most_recent_use"] = last_used

    # Identify inactive users
    inactive_users = []
    for record in user_usage.values():
        last_used = record["most_recent_use"]
        if not last_used or last_used.date() < thirty_days_ago:
            inactive_users.append(record["user"])

    return inactive_users
