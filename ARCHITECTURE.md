# Project Structure

```
RA_weather_agentic/
├── 📱 frontend/                    # Streamlit Web Interface
│   ├── app.py                     # Main Streamlit application
│   ├── requirements.txt           # Frontend dependencies
│   ├── Dockerfile                 # Frontend container
│   ├── run_frontend.py            # Frontend startup script
│   ├── .streamlit/
│   │   └── config.toml            # Streamlit configuration
│   └── README.md                  # Frontend documentation
│
├── 🧠 weather_outfit_ai/          # Core AI System
│   ├── 🎭 agents/                 # AI Agents
│   │   ├── supervisor_agent.py    # Routes user intent
│   │   ├── weather_agent.py       # Fetches weather data
│   │   ├── wardrobe_agent.py      # Selects clothing items
│   │   ├── design_agent.py        # Creates outfit recommendations
│   │   └── conversation_agent.py  # Generates responses
│   │
│   ├── 🔧 orchestrator/           # Pure Pydantic Orchestration
│   │   └── outfit_orchestrator.py # Replaces LangGraph workflow
│   │
│   ├── 📊 models/                 # Data Models
│   │   ├── state.py               # Agent state management
│   │   └── schemas.py             # Pydantic data schemas
│   │
│   ├── 🔗 services/               # External Services
│   │   ├── weather_service.py     # Weather API integration
│   │   └── wardrobe_service.py    # ChromaDB wardrobe storage
│   │
│   ├── 🗃️ graph/                  # Deprecated LangGraph (kept for reference)
│   │   ├── graph.py               # Deprecated wrapper
│   │   └── graph_deprecated.py    # Original LangGraph implementation
│   │
│   ├── app.py                     # FastAPI web server
│   ├── cli.py                     # Command-line interface
│   ├── config.py                  # Configuration management
│   └── prompts.py                 # AI agent prompts
│
├── 🛠️ utils/                      # Utilities
│   └── populate_wardrobe.py       # Initialize wardrobe database
│
├── 📊 data/                       # Sample Data
│   └── sample_wardrobe.csv        # Example clothing items
│
├── 🚀 run.py                      # Main application runner
├── 🐳 docker-compose.yml          # Full stack deployment
├── 📋 pyproject.toml              # Python project configuration
├── 🔒 env.example                 # Environment variables template
├── 📖 README.md                   # Main documentation
└── 📘 USAGE.md                    # Usage instructions
```

## Key Components

### 🎯 **Orchestrator (New)**
- **Pure Pydantic**: Type-safe, async workflow orchestration
- **Replaces LangGraph**: Simpler, more maintainable architecture
- **Memory Management**: Conversation history and thread management

### 🖥️ **Frontend (Streamlit)**
- **User-Friendly**: Simple web interface for outfit recommendations
- **Real-time**: Direct API communication with FastAPI backend
- **Responsive**: Works on desktop and mobile browsers
- **Docker-Ready**: Easy containerization and deployment

### 🔧 **Backend (FastAPI)**
- **REST API**: Clean HTTP endpoints for all functionality
- **Documentation**: Auto-generated API docs at `/docs`
- **Health Checks**: System status monitoring
- **Async Support**: High-performance async operations

### 🧠 **AI Agents**
- **Supervisor**: Intent analysis and workflow routing
- **Weather**: Real-time weather data retrieval
- **Wardrobe**: Smart clothing selection using RAG
- **Design**: Outfit recommendation generation
- **Conversation**: Natural language response formatting

### 📱 **Interface Options**
1. **Streamlit UI** (`http://localhost:8501`) - Recommended for users
2. **FastAPI Docs** (`http://localhost:8000/docs`) - For API testing
3. **CLI** (`python run.py chat`) - For terminal users

## Technology Stack

- **🐍 Python 3.10+**: Core runtime
- **🔧 Pydantic**: Data validation and orchestration
- **🌐 FastAPI**: REST API framework
- **📱 Streamlit**: Web UI framework
- **🤖 LangChain**: LLM integration (OpenAI)
- **🗄️ ChromaDB**: Vector database for wardrobe
- **🐳 Docker**: Containerization
- **⚡ UV**: Fast Python package management

## Architecture Benefits

### 🎯 **Pure Pydantic Orchestration**
- ✅ **Type Safety**: Full static type checking
- ✅ **Performance**: No framework overhead
- ✅ **Simplicity**: Easy to understand and modify
- ✅ **Testability**: Simple unit testing
- ✅ **Maintainability**: Clear data flow

### 📱 **Streamlit Frontend**
- ✅ **Rapid Development**: Built for AI/data apps
- ✅ **Low Maintenance**: Minimal frontend code
- ✅ **Docker-Friendly**: Easy containerization
- ✅ **Responsive**: Works across devices
- ✅ **Interactive**: Real-time user feedback

### 🔄 **Modular Design**
- ✅ **Pluggable**: Easy to swap components
- ✅ **Scalable**: Add new agents/features easily
- ✅ **Testable**: Independent component testing
- ✅ **Deployable**: Multiple deployment options
