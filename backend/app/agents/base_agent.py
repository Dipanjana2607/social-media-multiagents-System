from abc import ABC, abstractmethod

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage

from app.utils.llm_factory import get_llm
from app.utils.logger import get_logger

logger = get_logger("agents.base_agent")


class BaseAgent(ABC):
    def __init__(self, temperature: float = 0.7):
        self.llm : ChatGoogleGenerativeAI = get_llm(temperature)
        self.name: str = self.__class__.__name__

    ##This is a private method that every agent will have but the implementation will be same.
    # It takes a system prompt and a human prompt, constructs a conversation, and invokes the LLM to get a response. 
    # The response is then stripped of any leading or trailing whitespace and returned as a string.
    def _call_llm(self, system_prompt: str, human_prompt: str) -> str:
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            logger.info(f"{self.name}: calling LLM (system_len={len(system_prompt)} human_len={len(human_prompt)})")
            response = self.llm.invoke(messages)
            content = response.content.strip()
            logger.info(f"{self.name}: LLM returned (len={len(content)})")
            return content
        except Exception:
            logger.exception(f"{self.name}: error while calling LLM")
            raise
    
    #This is an abstract method that every agent will have but the implementation will be different for each agent.
    @abstractmethod
    def run(self, *args, **kwargs):
        pass
        