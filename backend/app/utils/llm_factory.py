from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("utils.llm_factory")


def get_llm(temperature: float = 0.7):
    logger.info(f"Creating LLM instance model=gemini-2.5-flash temperature={temperature} api_key_set={'yes' if bool(settings.google_api_key) else 'no'}")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.google_api_key, temperature=temperature)