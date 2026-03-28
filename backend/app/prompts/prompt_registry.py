from app.prompts.linkedin_prompts import LINKEDIN_PROMPTS
from app.prompts.twitter_prompts import TWITTER_PROMPTS
from app.prompts.instagram_prompts import INSTAGRAM_PROMPTS
from app.utils.logger import get_logger

logger = get_logger("prompts.prompt_registry")

PROMPT_REGISTRY = {
    "linkedin": LINKEDIN_PROMPTS,   
    "twitter": TWITTER_PROMPTS,
    "instagram": INSTAGRAM_PROMPTS,
}

def get_prompt(platform: str) -> dict:
    platform = platform.lower().strip()
    if platform not in PROMPT_REGISTRY:
        logger.warning(f"Unsupported platform requested: {platform}")
        raise ValueError(f"Unsupported platform: {platform}. Supported platforms are: {', '.join(PROMPT_REGISTRY.keys())}")
    
    logger.info(f"Providing prompts for platform: {platform}")
    return PROMPT_REGISTRY[platform]

def get_available_platforms() -> list[str]:
    return list(PROMPT_REGISTRY.keys())

