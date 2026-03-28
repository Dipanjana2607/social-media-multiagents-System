from app.agents.base_agent import BaseAgent

class VerifierAgent(BaseAgent):
    def __init__(self):
        super().__init__(temperature=0.2)
        self.name = "VerifierAgent"

    def run(self, prompt_config: dict, content: str, plan: str, topic: str ) -> tuple[bool,str]:
        system_prompt = prompt_config["system"]
        human_prompt = prompt_config["user"].format(content=content, plan=plan, topic=topic)

        response = self._call_llm(system_prompt, human_prompt)
        passed = "Verdict: Pass" in response.upper()
        
        return passed, response
    

    def extract_feedback(self, verdict_text: str) -> str:
        for line in verdict_text.split("\n"):
            if line.strip().upper().startswith("FEEDBACK:"):
                return line.split(":", 1)[1].strip()
        return ""
    
    def wants_full_restart(self, verdict_text: str) -> bool:
        return "RESTART_STAGE: PLANNER" in verdict_text.upper()