from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status
from app import models, schemas
from datetime import datetime
import uuid
from app.services.user_service import UserService

class ReferralService:
    def __init__(self, db: AsyncSession, redis_client, user_service: UserService):
        self.db = db
        self.redis_client = redis_client
        self.user_service = user_service

    async def create_referral_code(self, current_user, code_data: schemas.ReferalCodeCreate):
        existing_code = await self.db.execute(
            select(models.ReferralCode).where(models.ReferralCode.user_id == current_user.id)
        )
        existing_code = existing_code.scalar_one_or_none()
        if existing_code:
            raise HTTPException(status_code=400, detail="У вас уже есть активный реферальный код")
        code = str(uuid.uuid4())
        new_code = models.ReferralCode(
            code=code,
            expiration_date=code_data.expiration_date,
            user_id=current_user.id
        )
        self.db.add(new_code)
        await self.db.commit()
        await self.db.refresh(new_code)
        ttl = int((code_data.expiration_date - datetime.utcnow()).total_seconds())
        try:
            self.redis_client.setex(code, ttl, current_user.id)
        except Exception as e:
            print(f"Redis error: {e}")
        return new_code

    async def delete_referral_code(self, current_user):
        code = await self.db.execute(
            select(models.ReferralCode).where(models.ReferralCode.user_id == current_user.id)
        )
        code = code.scalar_one_or_none()
        if not code:
            raise HTTPException(status_code=404, detail="Реферальный код не найден")
        await self.db.execute(delete(models.ReferralCode).where(models.ReferralCode.id == code.id))
        await self.db.commit()
        try:
            self.redis_client.delete(code.code)
        except Exception as e:
            print(f"Redis error: {e}")

    async def get_referral_code_by_email(self, email: str):
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        code = await self.db.execute(
            select(models.ReferralCode).where(models.ReferralCode.user_id == user.id)
        )
        code = code.scalar_one_or_none()
        if not code:
            raise HTTPException(status_code=404, detail="Реферальный код не найден")
        return code

    async def register_with_referral(self, code: str, user_data: schemas.UserCreate):
        try:
            referrer_id = self.redis_client.get(code)
            if referrer_id:
                referrer_id = int(referrer_id)
            else:
                code_in_db = await self.db.execute(
                    select(models.ReferralCode).where(models.ReferralCode.code == code)
                )
                code_in_db = code_in_db.scalar_one_or_none()
                if not code_in_db or code_in_db.expiration_date < datetime.utcnow():
                    raise HTTPException(status_code=400, detail="Неверный или просроченный реферальный код")
                referrer_id = code_in_db.user_id
        except Exception as e:
            print(f"Redis error: {e}")
            code_in_db = await self.db.execute(
                select(models.ReferralCode).where(models.ReferralCode.code == code)
            )
            code_in_db = code_in_db.scalar_one_or_none()
            if not code_in_db or code_in_db.expiration_date < datetime.utcnow():
                raise HTTPException(status_code=400, detail="Неверный или просроченный реферальный код")
            referrer_id = code_in_db.user_id

        existing_user = await self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        try:
            new_user = await self.user_service.create_user(user_data)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        referral = models.Referral(
            referrer_id=referrer_id,
            referred_user_id=new_user.id
        )
        self.db.add(referral)
        await self.db.commit()
        return new_user

    async def get_referrals(self, referrer_id: int):
        referrals = await self.db.execute(
            select(models.Referral).where(models.Referral.referrer_id == referrer_id)
        )
        referrals = referrals.scalars().all()
        referral_ids = [referral.referred_user_id for referral in referrals]
        if not referral_ids:
            return []
        users = await self.db.execute(
            select(models.User).where(models.User.id.in_(referral_ids))
        )
        users = users.scalars().all()
        return users
