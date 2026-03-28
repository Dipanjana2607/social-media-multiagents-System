from app.agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0.5)
        self.name = "PlannerAgent"

    def run(self, prompt_config: dict,  topic: str, tone: str, extra: str = "") -> str:
        system_prompt = prompt_config["system"]
        human_prompt = prompt_config["user"].format(topic=topic, tone=tone, extra= extra or "None")

        return self._call_llm(system_prompt, human_prompt)