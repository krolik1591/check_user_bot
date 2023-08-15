from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, validator, SecretStr, RedisDsn


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_ids: str

    @validator("admin_ids")
    def is_admin(cls, v: str):
        return v.split(',')

    class Config:
        env_file = Path(__file__).parent.parent / '.env'
        env_file_encoding = 'utf-8'


config = Settings()
