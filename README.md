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
