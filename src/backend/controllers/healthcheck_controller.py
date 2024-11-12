from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from starlette.responses import JSONResponse

from src.database.adapters.mysql import MySQL

healthcheck_router = APIRouter(tags=["Health Check"])


@healthcheck_router.get("/healthcheck")
async def healthcheck():
    try:
        with MySQL.session() as session:
            db = session.execute(text("SELECT 1"))
            result = db.fetchone()
            assert result
            assert result[0] == 1
        return JSONResponse(
            content={"status": "ok", "db": "connected"}, status_code=200
        )
    except OperationalError:
        return JSONResponse(
            content={"status": "error", "db": "disconnected"}, status_code=500
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)}, status_code=500
        )
