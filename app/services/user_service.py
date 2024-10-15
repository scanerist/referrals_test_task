from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.utils.hashing import get_password_hash

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user: schemas.UserCreate):
        hashed_password = get_password_hash(user.password)
        db_user = models.User(email=user.email, hashed_password=hashed_password)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(models.User).where(models.User.email == email))
        return result.scalars().first()