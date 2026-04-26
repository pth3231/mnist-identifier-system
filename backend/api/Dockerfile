FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set workdir
WORKDIR /api

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtualenv
RUN python3 -m venv /api/.venv

# Set PATH, activate venv
ENV PATH="/api/.venv/bin:$PATH"

# Copy pyproject.toml
COPY pyproject.toml .

# Copy application code
COPY . .

RUN . /api/.venv/bin/activate && \
    pip install --upgrade pip setuptools wheel && \ 
    pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /api
USER appuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=15s \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run FastAPI app using the src package
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
