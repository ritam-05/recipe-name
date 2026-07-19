"""ChatOpenAI wrapper and related LLM helpers."""

from langchain_openai import ChatOpenAI

from app.config import settings


class LLMService:
    def __init__(self) -> None:
        self.client = ChatOpenAI(
            model=settings.model_name,
            temperature=settings.temperature,
            openai_api_key=settings.groq_api_key,
            openai_api_base=settings.groq_api_base,
        )

    def invoke(self, messages):
        return self.client.invoke(messages)
