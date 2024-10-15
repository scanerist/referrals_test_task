from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas
from app.database import get_db
from app.auth.oauth2 import get_current_user
from app.services.referal_service import ReferralService
from app.services.user_service import UserService
from app.core.config import settings
import redis


router = APIRouter()

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

@router.post("/create_code", response_model=schemas.ReferalCoderesponse)
async def create_referral_code(
    code_data: schemas.ReferalCodeCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    referral_service = ReferralService(db, redis_client, user_service)
    new_code = await referral_service.create_referral_code(current_user, code_data)
    return new_code

@router.delete("/delete_code", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referral_code(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    referral_service = ReferralService(db, redis_client, user_service)
    await referral_service.delete_referral_code(current_user)
    return

@router.get("/code/{email}", response_model=schemas.ReferalCodeCreate)
async def get_referral_code_by_email(email: str, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    referral_service = ReferralService(db, redis_client, user_service)
    code = await referral_service.get_referral_code_by_email(email)
    return code

@router.post("/register/{code}", response_model=schemas.UserResponse)
async def register_with_referral(
    code: str,
    user_data: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    referral_service = ReferralService(db, redis_client, user_service)
    new_user = await referral_service.register_with_referral(code, user_data)
    return new_user

@router.get("/referrals/{referrer_id}", response_model=list[schemas.UserResponse])
async def get_referrals(referrer_id: int, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    referral_service = ReferralService(db, redis_client, user_service)
    users = await referral_service.get_referrals(referrer_id)
    return users
