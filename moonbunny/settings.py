from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="moonbunny_",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="allow",
    )
