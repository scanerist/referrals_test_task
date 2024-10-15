from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from app.utils.hashing import verify_password
from app.auth.jwt import create_access_token
from datetime import timedelta
from app.services.user_service import UserService
from app.core.config import settings
from app.database import get_db

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    existing_user = await user_service.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user)

@router.post("/login", response_model=schemas.Token)
async def login(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user_in_db = await user_service.get_user_by_email(email=user.email)
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
