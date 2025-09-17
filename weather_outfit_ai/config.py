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
            os.environ["LANGCHAIN_TRACING_V2"] = self.LANGSMITH_TRACING
            os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
            os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

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
            "LANGSMITH_API_KEY": "***" if self.LANGSMITH_API_KEY else None,
            "LANGSMITH_PROJECT": self.LANGSMITH_PROJECT,
            "LANGSMITH_TRACING": self.LANGSMITH_TRACING,
            "WEATHER_API_KEY": "***" if self.WEATHER_API_KEY else None,
        }


# Global config instance
config = Config()
