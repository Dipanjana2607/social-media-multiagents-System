from fastapi import APIRouter, HTTPException
from app.dtos.request_dtos import GenerateContentRequest
from app.dtos.response_dtos import GenerateContentResponse
from app.services.content_service import ContentService
from app.prompts.prompt_registry import get_available_platforms
from app.utils.logger import get_logger

logger = get_logger("controllers.content_controller")

# One router, one prefix — no more /linkedin, /twitter, /instagram routes
router = APIRouter(prefix="/content", tags=["Content Generation"])

# One service instance shared across all requests
service = ContentService()

@router.post("/generate", response_model=GenerateContentResponse)
async def generate_content(request: GenerateContentRequest):
    logger.info(f"generate_content called: platform={request.platform} topic={request.topic} max_retries={request.max_retries}")
    try:
        result = service.generate(request)
        logger.info(f"generate_content success: platform={request.platform} attempts={result.total_attempts} success={result.success}")
        return result
    except ValueError as e:
        # ValueError is raised by get_prompts() if the platform is unknown
        logger.warning("ValueError in generate_content", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Any other error becomes a 500 Internal Server Error
        logger.exception("Unhandled exception in generate_content")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/platforms")
async def list_platforms():
    logger.info("list_platforms called")
    platforms = get_available_platforms()
    logger.info(f"available platforms: {platforms}")
    return {"available_platforms": platforms}