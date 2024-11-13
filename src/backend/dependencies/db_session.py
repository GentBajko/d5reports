from src.database.interfaces.session import ISession
from src.database.sessions.sqlalchemy_session import SQLAlchemySession
from src.database.adapters.mysql import MySQL


async def get_session() -> ISession:
    wrapped_session = SQLAlchemySession(MySQL.session())
    return wrapped_session
