from app.agents.base_agent import BaseAgent

class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0.7)
        self.name = "ExecutorAgent"

    def run(self, prompt_config: dict, plan: str, topic: str, tone: str) -> str:
        system_prompt = prompt_config["system"]
        human_prompt = prompt_config["user"].format(plan=plan, topic=topic, tone=tone)
        
        return self._call_llm(system_prompt, human_prompt)