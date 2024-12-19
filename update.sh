systemctl stop fastapi
git pull
uv run alembic upgrade head
systemctl daemon-reload
systemctl restart fastapi