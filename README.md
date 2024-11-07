# Setup

## Install UV Package Manager

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install Python Using UV

```sh
uv python install 3.12
```

## Install Dependencies

### Local Env

```sh
uv sync
```

### On Deployment
```sh
uv sync --no-dev
```
## Database Setup
The setup uses alembic (aleady installed by uv with `uv sync`). Ideally to develop locally in a more reliable/easy way you should use docker.

### Run MySQL on Docker
```sh
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=d5report \
  -e MYSQL_DATABASE=reports \
  -e MYSQL_USER=d5 \
  -e MYSQL_PASSWORD=d5report \
  -p 3306:3306 \
  mysql:latest
```
Replace the values with whatever you are using in your `.env` file.

### Apply Previous Migrations Into The DB
```sh
alembic upgrade head
```
This is included as a step during deployment to always keep the DB up to date.

### Apply New Migration
```sh
uv run alembic revision --autogenerate -m "some_commit_mesage"
```
Finish off with:
```sh
alembic upgrade head
```
### Delete Migration
Revert the latest migration:
```sh
alembic downgrade -1
```
Remove the newly generated migration script:
```sh
rm alembic/versions/<migration_filename>.py
```

# Run Application

## Run the Backend
```sh
uv run main.py
```