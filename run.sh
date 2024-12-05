uv run gunicorn src.backend.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
