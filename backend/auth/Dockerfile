# ============ Stage 1: Builder ============
FROM python:3.12-slim AS builder
WORKDIR /auth

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Cache mount added to drastically speed up repeated builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ============ Stage 2: Runtime ============
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/auth/.venv/bin:$PATH"

WORKDIR /auth

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

# Only copy the virtual environment
COPY --from=builder /auth/.venv /auth/.venv

# Copy application code
COPY ./models/ ./models/
COPY ./routes/ ./routes/
COPY ./utils/ ./utils/
COPY main.py config.py ./

# Run as non-root user
RUN useradd -m authuser || true
USER authuser

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]