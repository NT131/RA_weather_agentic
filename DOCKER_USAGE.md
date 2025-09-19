# Docker Usage Guide

This guide explains how to use all three components of the Weather Outfit AI system through Docker:

## 🏗️ Complete Setup

### 1. Environment Configuration
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY, WEATHER_API_KEY
# Optional: LANGSMITH_API_KEY, LANGSMITH_PROJECT
```

### 2. Build All Services
```bash
# Build all Docker images
docker-compose build
```

## 🚀 Usage Options

### Option 1: Web Application Stack (Recommended)
Run both the FastAPI backend and Streamlit frontend:

```bash
# Start the full web stack
docker-compose up

# Or run in detached mode
docker-compose up -d

# Access the applications:
# - Streamlit Frontend: http://localhost:8501
# - FastAPI Backend: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### Option 2: Backend Only
Run just the FastAPI backend for API access:

```bash
# Start only the backend service
docker-compose up backend

# Test the API:
curl http://localhost:8000/health
```

### Option 3: CLI Tool
Use the command-line interface for terminal-based interactions:

```bash
# Start interactive CLI session
docker-compose --profile cli run --rm cli

# Or run specific CLI commands:
docker-compose --profile cli run --rm cli python run.py chat
docker-compose --profile cli run --rm cli python run.py recommend -m "What should I wear in New York today?"
```

### Option 4: One-off CLI Commands
For quick recommendations without interactive mode:

```bash
# Single recommendation
docker-compose --profile cli run --rm cli python run.py recommend \
  -m "What should I wear in San Francisco?" \
  -l "San Francisco, CA" \
  -c "Going to work"

# Start chat mode
docker-compose --profile cli run --rm cli python run.py chat
```

## 📊 Service Details

### 🔧 Backend Service (`backend`)
- **Port**: 8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Environment**: Requires OPENAI_API_KEY, WEATHER_API_KEY

### 📱 Frontend Service (`frontend`)
- **Port**: 8501
- **Health Check**: http://localhost:8501/_stcore/health
- **Depends on**: Backend service
- **Environment**: API_URL automatically configured

### 💻 CLI Service (`cli`)
- **Profile**: `cli` (requires --profile cli to run)
- **Interactive**: stdin_open: true, tty: true
- **Volume**: Shares wardrobe_db with host
- **Environment**: Same as backend

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up --build
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   lsof -i :8000  # Backend
   lsof -i :8501  # Frontend
   ```

2. **Environment Variables**
   ```bash
   # Verify .env file exists and has required keys
   cat .env
   ```

3. **API Key Issues**
   ```bash
   # Test backend health
   curl http://localhost:8000/health
   
   # Check backend logs
   docker-compose logs backend
   ```

4. **CLI Not Working**
   ```bash
   # Ensure you use the cli profile
   docker-compose --profile cli run --rm cli python run.py chat
   ```

### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 🎯 Recommended Workflows

### Development
```bash
# Start backend and frontend for web development
docker-compose up backend frontend

# Use CLI for testing
docker-compose --profile cli run --rm cli python run.py chat
```

### Production
```bash
# Start all web services in detached mode
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

### Testing
```bash
# Quick CLI test
docker-compose --profile cli run --rm cli python run.py recommend -m "Test message"

# API test
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What should I wear today?"}'
```

## 📋 Service Dependencies

- **Frontend** depends on **Backend**
- **CLI** is independent (uses direct orchestrator)
- All services share the same environment configuration
- Wardrobe database is shared between backend and CLI via volume mount

This setup provides maximum flexibility for development, testing, and production use of the Weather Outfit AI system.
