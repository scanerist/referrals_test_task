from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = '.env.example'
        env_file_encoding = 'utf-8'


settings = Settings()