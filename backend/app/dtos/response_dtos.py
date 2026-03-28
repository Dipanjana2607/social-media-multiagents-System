from pydantic import BaseModel
from typing import List, Optional

class AgentStepResult(BaseModel):
    agent_name: str
    output: str
    attempts: int

class GenerateContentResponse(BaseModel):
    platform: str
    topic: str
    tone: str
    final_content: str
    agent_steps: List[AgentStepResult]
    total_attempts: int
    success: bool
    
    
