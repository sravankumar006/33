from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./tech_decision.db'
    frontend_url: AnyHttpUrl = 'http://localhost:3000'
    openai_api_key: str = ''

    @field_validator('database_url', mode='before')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith('postgresql://'):
            return v.replace('postgresql://', 'postgresql+psycopg://', 1)
        return v

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
