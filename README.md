# Weather Outfi### Frontend Options
- **🖥️ Streamlit UI**: User-friendly web interface with both form and chat modes
  - **📝 Form Mode**: Quick structured outfit recommendations  
  - **💬 Chat Mode**: Natural language conversations about fashion
- **🔧 FastAPI**: REST API for integrations and custom frontends
- **💻 CLI**: Command-line interface for terminal users 🌤️👕

An intelligent AI system that provides personalized outfit recommendations based on real-time weather data. Built with **FastAPI**, **Streamlit**, and **Pure Pydantic Orchestration** for reliable, agentic AI interactions.

## 🏗️ Architecture

### AI Agent System
The system uses **Pure Pydantic Orchestration** to coordinate 5 specialized agents:

1. **👥 Supervisor Agent**: Analyzes user input and extracts location/context using JSON
2. **🌡️ Weather Agent**: Retrieves real-time weather data with structured JSON output
3. **👔 Wardrobe Agent**: Intelligently selects clothing items using RAG (Retrieval-Augmented Generation)
4. **🎯 Design Agent**: Creates outfit recommendations using simplified pipe-separated format
5. **💬 Conversation Agent**: Generates natural, conversational responses

### Frontend Options
- **�️ Streamlit UI**: User-friendly web interface (recommended for most users)
- **🔧 FastAPI**: REST API for integrations and custom frontends
- **💻 CLI**: Command-line interface for terminal users

## �🚀 Quick Start

### Option 1: Full Stack (Recommended)

```bash
# 1. Install dependencies
uv sync

# 2. Set up environment variables (see below)
cp env.example .env
# Edit .env with your API keys

# 3. Initialize the wardrobe database
uv run python utils/populate_wardrobe.py

# 4. Start the backend (Terminal 1)
uv run python run.py web

# 5. Start the frontend (Terminal 2)
uv run python run.py frontend
```

**Access the application:**
- **Frontend UI**: http://localhost:8501 (Streamlit interface)
- **API**: http://localhost:8000 (FastAPI backend)
- **API Docs**: http://localhost:8000/docs

### Option 2: Docker Compose (Easy Deployment)

```bash
# Build and run both services
docker-compose up --build

# Access at:
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
```

### Prerequisites
- **Python 3.10+** with **UV** (recommended) OR **Docker & Docker Compose**
- **OpenAI API Key** (required)
- **Weather API Key** (optional, uses free tier by default)
- **LangSmith API Key** (optional, for tracing)

## 🔑 Environment Variables & API Keys

Create a `.env` file in the project root with the following variables:

```env
# Required - OpenAI API for LLM functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional - LangSmith for advanced tracing and monitoring
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=weather-outfit-ai

WEATHER_API_KEY=your_weather_api_key_here
```

### 🔐 How to Get API Keys

#### 1. OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key and add it to your `.env` file

#### 2. LangSmith API Key (Optional - for observability)
1. Visit [LangSmith](https://smith.langchain.com/)
2. Sign up with your email or GitHub account
3. Go to **Settings** → **API Keys**
4. Click **"Create API Key"**
5. Copy both the API key and set a project name
6. Add both to your `.env` file

#### 3. Weather API Key
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to your dashboard/API keys section
4. Copy your free API key
5. Add it to your `.env` file



## 💻 Local Development Setup

### 1. Install Dependencies
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Initialize the Wardrobe Database
```bash
uv run python utils/populate_wardrobe.py
```

### 3. Run the Application

#### Full Stack Development
```bash
# Terminal 1: Backend API
uv run python run.py web

# Terminal 2: Frontend UI  
uv run python run.py frontend

# Terminal 3: CLI (optional)
uv run python run.py chat
```

#### Individual Services
```bash
# Just the API
uv run uvicorn weather_outfit_ai.app:app --reload

# Just the CLI
uv run python weather_outfit_ai/cli.py chat

# Just the frontend
cd frontend && streamlit run app.py
```

## 🎯 Usage Examples

### Web Interface (Streamlit)

#### Form Mode
1. Go to http://localhost:8501
2. Keep "📝 Form Mode" selected
3. Enter location (e.g., "New York")
4. Select style preference
5. Click "Get Outfit Recommendation"

#### Chat Mode
1. Go to http://localhost:8501  
2. Switch to "💬 Chat Mode"
3. Type natural language messages:
   - "What should I wear in London today?"
   - "I have a meeting in NYC tomorrow, outfit suggestions?"
   - "It's raining, what should I wear?"

### API Usage
```bash
curl -X POST "http://localhost:8000/outfit-recommendation" \
     -H "Content-Type: application/json" \
     -d '{"location": "New York", "style_preference": "business"}'
```

### CLI Usage
```bash
# Interactive chat
uv run python run.py chat

# Single recommendation
uv run python run.py recommend "What should I wear in London today?"
```


## 🤖 AI Response Formats

### Design Agent Output
```
Blue Cotton T-Shirt|Dark Jeans|White Sneakers|None|Watch,Sunglasses
```
**Format**: `top|bottom|footwear|outerwear|accessories`

### Outfit Judge Output  
```
8.5|7.0|9.0|8.0|Great color coordination and weather appropriateness
```
**Format**: `color_score|style_score|appropriateness_score|overall_score|summary`

### Weather Agent Output
```json
{
  "weather_analysis": "Pleasant mild weather with clear skies",
  "comfort_level": 4,
  "key_factors": ["temperature", "humidity", "wind"],
  "recommendations": "Light layers recommended"
}
```

## 🔧 Configuration

### Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for LLM functionality | - |
| `LANGSMITH_API_KEY` | ❌ Optional | LangSmith API key for tracing | - |
| `LANGSMITH_PROJECT` | ❌ Optional | LangSmith project name | `weather-outfit-ai` |
| `WEATHER_API_KEY` | ✅ Yes  | Weather service API key | Uses free tier |

### Customizing the System

1. **Add Wardrobe Items**: Edit `data/sample_wardrobe.csv` and run `python utils/populate_wardrobe.py`
2. **Modify Agent Prompts**: Update prompts in `weather_outfit_ai/prompts.py`

