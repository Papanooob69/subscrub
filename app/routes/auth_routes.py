from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Response
from app.core import security
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.models import user_models
from app.schemas import auth_schemas
from app.dependencies.auth_dependencies import get_current_user

router = APIRouter()


@router.post("/register")
def register_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(user_models.User).filter_by(email=user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    crud.create_user(db=db, user=user)
    return {"message": "User created successfully"}


@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(user_models.User).filter(
        user_models.User.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = security.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def read_user_me(current_user: int = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }
