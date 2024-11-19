from database.adapters.mysql import MySQL
from database.interfaces.session import ISession
from database.sessions.sqlalchemy_session import SQLAlchemySession


async def get_session() -> ISession:
    wrapped_session = SQLAlchemySession(MySQL.session())
    return wrapped_session
