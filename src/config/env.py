from pydantic.v1 import Field, BaseSettings


class EnvironmentConfig(BaseSettings):
    API_PORT: int = Field(default=..., env="API_PORT")
    API_URL: str = Field(default=..., env="API_URL")

    DB_USER: str = Field(default=..., env="DB_USER")
    DB_PASSWORD: str = Field(default=..., env="DB_PASSWORD")
    DB_HOST: str = Field(default=..., env="DB_HOST")
    DB_PORT: int = Field(default=..., env="DB_PORT")
    DB_NAME: str = Field(default=..., env="DB_NAME")

    LOGURU_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


CONFIG = EnvironmentConfig()

__all__ = ["CONFIG", "EnvironmentConfig"]
