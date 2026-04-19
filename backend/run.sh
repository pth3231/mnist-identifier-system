#!/bin/bash
# Japanese Character Identifier - Development Server Runner

set -e

cd "$(dirname "$0")"

echo "=== Japanese Character Identifier API ==="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[!] .env not found. Copying from .env.example..."
    cp .env.example .env
    echo "[!] Please edit .env with your configuration before running again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[*] Installing dependencies..."
pip install -q -e ".[dev]"

# Run the server
echo "[*] Starting development server..."
echo ""
echo "API available at: http://localhost:8000"
echo "Swagger docs: http://localhost:8000/docs"
echo ""

uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
