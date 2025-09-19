FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY . .

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH="/app:$PYTHONPATH"

RUN mkdir -p wardrobe_db

EXPOSE 8000

# Default command runs the web server, but can be overridden for CLI usage
CMD ["sh", "-c", "echo 'Weather Outfit AI - Backend Startup' && echo '======================================' && echo 'Populating wardrobe with sample data...' && python utils/populate_wardrobe.py && echo 'Starting FastAPI backend...' && python -m uvicorn weather_outfit_ai.app:app --host 0.0.0.0 --port 8000"] 