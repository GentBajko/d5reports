from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.env import ENV


class MySQL:
    __driver = "mysql+pymysql"
    __host = ENV.DB_HOST
    __port = ENV.DB_PORT
    __user = ENV.DB_USER
    __password = ENV.DB_PASSWORD
    __db = ENV.DB_NAME
    url = f"{__driver}://{__user}:{__password}@{__host}:{__port}/{__db}"
    engine = create_engine(url)

    Session = sessionmaker(bind=engine)

    @classmethod
    def session(cls):
        return cls.Session()
