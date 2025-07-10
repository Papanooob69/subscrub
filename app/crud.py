from sqlalchemy.orm import Session
from app.models import user_models
from app.core import security
from app.schemas import auth_schemas
from app.schemas.tool_schemas import ToolRead
from app.models.user_models import Tool


def create_user(db: Session, user: auth_schemas.UserCreate):
    hashed_password = security.hash_password(user.password)
    db_user = user_models.User(
        email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_tools(db: Session, user_id: int):
    return db.query(Tool).filter(Tool.owner_id == user_id).all()
