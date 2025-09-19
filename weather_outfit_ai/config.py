import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """Simple application configuration."""

    def __init__(self) -> None:
        """Initialize configuration and set up LangSmith environment if needed."""
        self._setup_langsmith_environment()

    @property
    def OPENAI_API_KEY(self) -> str:  # noqa: N802
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def OPENAI_MODEL(self) -> str:  # noqa: N802
        """Get OpenAI model name from environment."""
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def OPENAI_TEMPERATURE(self) -> float:  # noqa: N802
        """Get OpenAI temperature from environment."""
        try:
            return float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        except ValueError:
            return 0.7

    @property
    def LANGSMITH_API_KEY(self) -> str:  # noqa: N802
        """Get LangSmith API key from environment."""
        return os.getenv("LANGSMITH_API_KEY", "")

    @property
    def LANGSMITH_PROJECT(self) -> str:  # noqa: N802
        """Get LangSmith project name from environment."""
        return os.getenv("LANGSMITH_PROJECT", "weather-outfit-ai")

    @property
    def LANGSMITH_TRACING(self) -> str:  # noqa: N802
        """Get LangSmith tracing setting from environment."""
        return os.getenv("LANGSMITH_TRACING", "true")

    @property
    def LANGSMITH_WORKSPACE_ID(self) -> str | None:  # noqa: N802
        """Get LangSmith workspace ID from environment."""
        return os.getenv("LANGSMITH_WORKSPACE_ID")

    @property
    def WEATHER_API_KEY(self) -> str | None:  # noqa: N802
        """Get Weather API key from environment."""
        return os.getenv("WEATHER_API_KEY")

    @property
    def LOG_LEVEL(self) -> str:  # noqa: N802
        """Get log level from environment."""
        return os.getenv("LOG_LEVEL", "INFO")

    def _setup_langsmith_environment(self) -> None:
        """Set up LangSmith environment variables only when LangSmith is configured."""
        if self.LANGSMITH_API_KEY:
            try:
                os.environ["LANGCHAIN_TRACING_V2"] = self.LANGSMITH_TRACING
                os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
                os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
                os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
                
                # Set workspace ID if provided (required for org-scoped keys)
                if self.LANGSMITH_WORKSPACE_ID:
                    os.environ["LANGSMITH_WORKSPACE_ID"] = self.LANGSMITH_WORKSPACE_ID
                
                print(f"✅ LangSmith tracing enabled for project: {self.LANGSMITH_PROJECT}")
                if self.LANGSMITH_WORKSPACE_ID:
                    print(f"🏢 Using workspace ID: {self.LANGSMITH_WORKSPACE_ID}")
                    
            except Exception as e:
                print(f"⚠️  Warning: LangSmith setup failed: {e}")
                self._disable_langsmith()
        else:
            print("📝 LangSmith tracing disabled (no API key provided)")

    def _disable_langsmith(self) -> None:
        """Disable LangSmith tracing."""
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        for key in ["LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT", "LANGCHAIN_ENDPOINT", "LANGSMITH_WORKSPACE_ID"]:
            if key in os.environ:
                del os.environ[key]
        print("🚫 LangSmith tracing disabled due to configuration issues")

    def validate(self) -> None:
        """Validate required configuration."""
        if not self.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in your .env file or environment variables."
            )

    def get_all_settings(self) -> dict:
        """Get all configuration settings for debugging."""
        return {
            "LOG_LEVEL": self.LOG_LEVEL,
            "OPENAI_API_KEY": "***" if self.OPENAI_API_KEY else None,
            "OPENAI_MODEL": self.OPENAI_MODEL,
            "OPENAI_TEMPERATURE": self.OPENAI_TEMPERATURE,
            "LANGSMITH_API_KEY": "***" if self.LANGSMITH_API_KEY else None,
            "LANGSMITH_PROJECT": self.LANGSMITH_PROJECT,
            "LANGSMITH_TRACING": self.LANGSMITH_TRACING,
            "LANGSMITH_WORKSPACE_ID": "***" if self.LANGSMITH_WORKSPACE_ID else None,
            "WEATHER_API_KEY": "***" if self.WEATHER_API_KEY else None,
        }


# Global config instance
config = Config()
