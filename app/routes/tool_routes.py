from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, status, Path, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user_models import Tool, User
from app.models.tool_assignment import ToolAssignment
from app.schemas.tool_schemas import ToolCreate, ToolRead, ToolUpdate, ToolUserUsage
from app.schemas.auth_schemas import UserRead
from app.dependencies.auth_dependencies import get_current_user
from app.crud import get_user_tools

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_tool(tool_data: ToolCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_tool = Tool(
        name=tool_data.name,
        price=tool_data.price,
        billing_cycle=tool_data.billing_cycle,
        renewal_date=tool_data.renewal_date,
        owner_id=current_user.id
    )
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    return new_tool


@router.get("/", response_model=List[ToolRead])
def list_tools(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_tools(db, user_id=current_user.id)


@router.put("/{tool_id}", response_model=ToolRead)
def update_tool(tool_id: int, tool_update: ToolUpdate = Body(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in tool_update.dict(exclude_unset=True).items():
        setattr(tool, field, value)
    db.commit()
    db.refresh(tool)
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool(tool_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(tool)
    db.commit()


@router.post("/{tool_id}/assign_user", status_code=200)
def assign_user_to_tool(tool_id: int, user_id: int = Body(..., embed=True), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(ToolAssignment).filter_by(
        tool_id=tool.id, user_id=user.id).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="User already assigned to this tool")

    assignment = ToolAssignment(tool_id=tool.id, user_id=user.id)
    db.add(assignment)
    db.commit()
    return {"message": f"User {user.email} assigned to tool '{tool.name}'"}


@router.get("/{tool_id}/users", response_model=List[UserRead])
def get_tool_users(tool_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    assignments = db.query(ToolAssignment).filter_by(tool_id=tool.id).all()
    return [a.user for a in assignments]


@router.post("/{tool_id}/mark_used", status_code=200)
def mark_tool_used(tool_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignment = db.query(ToolAssignment).filter_by(
        tool_id=tool_id, user_id=current_user.id).first()
    if not assignment:
        raise HTTPException(
            status_code=403, detail="You are not assigned to this tool")

    assignment.last_used_at = date.today()
    db.commit()
    return {"message": "Marked tool as used today."}


@router.get("/{tool_id}/usage", response_model=List[ToolUserUsage])
def get_tool_usage(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    thirty_days_ago = date.today() - timedelta(days=30)

    assignments = db.query(ToolAssignment).options(
        joinedload(ToolAssignment.user)
    ).filter_by(tool_id=tool.id).all()

    usage_data = []
    for a in assignments:
        # datetime -> date conversion
        last_used_date = a.last_used_at.date() if a.last_used_at else None
        is_active = last_used_date and last_used_date >= thirty_days_ago
        usage_status = "Active" if is_active else "Inactive"

        usage_data.append(
            ToolUserUsage(
                email=a.user.email,
                assigned_date=a.assigned_at.date() if a.assigned_at else None,
                last_used=last_used_date,
                status=usage_status
            )
        )

    return usage_data
