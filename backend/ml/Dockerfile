FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --upgrade pip setuptools && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install -e .

COPY mnist_model.pth /models/mnist_model.pth

EXPOSE 8001

CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8001"]