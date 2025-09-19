# Weather Outfit AI - Frontend

A simple, user-friendly Streamlit interface for the Weather Outfit AI system.

## Features

- 🎯 **Form Mode**: Quick outfit recommendations with structured inputs
- 💬 **Chat Mode**: Natural language conversations about fashion and weather  
- 🌤️ Real-time weather information display
- 📚 Recommendation history
- ⚙️ Configurable API endpoint
- 🏥 API health monitoring
- 📱 Responsive design
- 🔄 Seamless mode switching

## Quick Start

### Prerequisites

Make sure the FastAPI backend is running:
```bash
# From the project root
uv run uvicorn weather_outfit_ai.app:app --host 0.0.0.0 --port 8000
```

### Option 1: Direct Python Run

```bash
# Install dependencies
pip install streamlit requests

# Run the frontend
python run_frontend.py
```

### Option 2: Using UV (Recommended)

```bash
# From project root
uv sync
uv run python frontend/run_frontend.py
```

### Option 3: Direct Streamlit

```bash
cd frontend
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

The frontend will be available at: http://localhost:8501

## Docker Usage

### Build the frontend container

```bash
cd frontend
docker build -t weather-outfit-ai-frontend .
```

### Run the frontend container

```bash
docker run -p 8501:8501 weather-outfit-ai-frontend
```

### Using Docker Compose (Full Stack)

Create a `docker-compose.yml` in the project root:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    env_file:
      - .env

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - API_URL=http://backend:8000
```

Then run:
```bash
docker-compose up
```

## Configuration

The frontend automatically detects the API URL. You can configure it in the sidebar:

- **Default**: `http://localhost:8000`
- **Docker**: `http://backend:8000` (when using docker-compose)
- **Custom**: Any URL where your FastAPI backend is running

## Usage

### Form Mode
1. **Enter Location**: Type the city or location (e.g., "New York", "London")
2. **Select Style**: Choose your preferred style (casual, business, formal, etc.)
3. **Choose Time**: Select when you need the outfit (now, today, tomorrow, etc.)
4. **Get Recommendation**: Click the button to get your personalized outfit

### Chat Mode
1. **Switch to Chat**: Select "💬 Chat Mode" from the dropdown
2. **Natural Conversation**: Type natural language messages like:
   - "What should I wear in London today?"
   - "I have a business meeting in New York tomorrow, what outfit do you recommend?"
   - "It's raining in Seattle, what should I wear?"
   - "Tell me about the weather in Tokyo"
3. **Interactive Dialog**: Continue the conversation with follow-up questions
4. **History**: Your chat history is preserved during the session

## Features Explained

### Form Mode
- **Structured Input**: Traditional form-based interface
- **Quick Setup**: Predefined options for style and timing
- **Visual Results**: Weather cards and organized outfit display

### Chat Mode  
- **Natural Language**: Talk to the AI like you would a fashion consultant
- **Context Aware**: Remembers conversation history within the session
- **Multi-Purpose**: Ask about weather, outfits, or general fashion advice
- **Interactive**: Follow-up questions and clarifications

### Weather Information
- Real-time temperature and "feels like" temperature
- Humidity percentage  
- Wind speed
- Weather description

### Outfit Recommendations
- Detailed outfit suggestions based on weather and preferences
- Style-appropriate clothing recommendations
- Additional tips and advice

### History
- **Form Mode**: Keeps track of your last 10 structured recommendations
- **Chat Mode**: Maintains conversation flow during session
- Shows timestamp, location, style, and weather conditions
- Expandable entries for easy review

### Health Monitoring
- Real-time API health check in the sidebar
- Clear error messages if the backend is not available
- Instructions for starting the backend

## Architecture

The frontend is built with:
- **Streamlit**: Main framework for the web interface
- **Requests**: HTTP client for API communication
- **Python 3.11+**: Runtime environment

## Customization

### Styling
Edit `frontend/.streamlit/config.toml` to customize:
- Colors and theme
- Server configuration
- Browser behavior

### Layout
Modify `frontend/app.py` to change:
- Page layout and structure
- UI components and styling
- API interaction logic

## Troubleshooting

### "API Error" in Sidebar
- Make sure the FastAPI backend is running
- Check the API URL in the sidebar
- Verify the backend is accessible from the frontend

### "Import streamlit could not be resolved"
- Install dependencies: `pip install streamlit requests`
- Or use UV: `uv sync`

### Port Already in Use
```bash
# Kill processes on port 8501
lsof -t -i tcp:8501 | xargs kill -9

# Or use a different port
streamlit run app.py --server.port 8502
```

## Development

### Adding New Features
1. Modify `frontend/app.py`
2. Test locally with `streamlit run app.py`
3. Update Docker image if needed

### API Integration
The frontend uses the following API endpoints:
- `GET /health` - Health check
- `POST /outfit-recommendation` - Get outfit recommendation

See the main project README for API documentation.
