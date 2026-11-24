FROM python:3.14-alpine AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=0 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"

FROM base AS dev
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-install-project
COPY . .
CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS prod_dep
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-install-project

FROM prod_dep AS prod
COPY . .
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]