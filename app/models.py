from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id  = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    referals_code = relationship("Referral", back_populates="user")
    referals = relationship("User", back_populates="referals_code", foreign_keys="Referral.referer_id")



class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="referals_code")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    referer_id = Column(Integer, ForeignKey("users.id"))
    referef_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    referer = relationship("User", back_populates="referals")
    refered_user = relationship("User", foreign_keys=[referef_user_id])
