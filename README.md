# Weather Outfit AI 🌤️👕

An intelligent AI system that provides personalized outfit recommendations based on real-time weather data. Built with FastAPI, Next.js, and LangGraph for reliable, agentic AI interactions.

## 🏗️ Architecture

### AI Agent System
The system uses **LangGraph** to orchestrate 5 specialized agents:

1. **👥 Supervisor Agent**: Analyzes user input and extracts location/context using JSON
2. **🌡️ Weather Agent**: Retrieves real-time weather data with structured JSON output
3. **👔 Wardrobe Agent**: Intelligently selects clothing items using RAG (Retrieval-Augmented Generation)
4. **🎯 Design Agent**: Creates outfit recommendations using simplified pipe-separated format
6. **💬 Conversation Agent**: Generates natural, conversational responses

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended) OR
- **Python 3.9+** and **Node.js 18+** for local development
- **OpenAI API Key** (required)
- **LangSmith API Key** (optional, for tracing)
- **Weather API Key** (optional, uses free tier by default)

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

Create your environment
Initialize the chromadb, with example clothing by running the populate_wardrobe script

Implement the first step being the LangGraph graph in the 'graph/graph.py' file.
Write a simple script to use the graph as entry point for interaction with the workflow.

```bash
uv sync

uv run python utils/populate_wardrobe.py

# after completing the first steps of implementing a graph and app script
uv run python weather_outfit_ai/app.py
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

