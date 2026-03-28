from pydantic import BaseModel, Field
from typing import Optional

class GenerateContentRequest(BaseModel):
    platform: str = Field(..., description="Target platforms: twitter, linkedin, instagram")
    topic: str = Field(..., description="Topic for the content")
    tone: str = Field("professional", description="Tone of the content: professional, casual, humorous, etc.")
    extra: Optional[str] = Field(None, description="Any additional information or requirements for the content")
    max_retries: int = Field(3, description="Maximum number of retries for content generation in case of failure")