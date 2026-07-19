"""Environment and model configuration."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    groq_api_base: str = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
    model_name: str = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
    temperature: float = float(os.getenv("TEMPERATURE", "0.5"))


settings = Settings()
