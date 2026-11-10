# syntax=docker/dockerfile:1

# ---------- base: shared settings ----------
FROM python:3.12-slim-trixie AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# ---------- builder: has uv, builds the venv ----------
FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Only the dependency files, so this layer is cached until they change
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ---------- dev: hot reload, code comes from a bind mount ----------
FROM builder AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project   # adds dev dependencies
EXPOSE 8000
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]

# ---------- prod: small runtime image, no uv, non-root ----------
FROM base AS prod
RUN useradd --system --uid 1000 --no-create-home appuser
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]