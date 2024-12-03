from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from config.env import ENV


class MySQL:
    url = URL.create(
        drivername="mysql+pymysql",
        username=ENV.DB_USER,
        password=ENV.DB_PASSWORD,
        host=ENV.DB_HOST,
        port=int(ENV.DB_PORT),
        database=ENV.DB_NAME,
        query={"charset": "utf8mb4"},
    )
    logger.info(
        f"Connecting to {ENV.DB_NAME} at {ENV.DB_HOST}:{ENV.DB_PORT} as {ENV.DB_USER}"
    )
    engine = create_engine(url, pool_pre_ping=True, echo=False, future=True)
    Session = sessionmaker(bind=engine)

    @classmethod
    def session(cls):
        return cls.Session()
