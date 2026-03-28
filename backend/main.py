from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.content_controller import router as content_router
from app.utils.logger import setup_logging

# initialize logging early so imports and app startup are captured
setup_logging()

app = FastAPI(
    title="Social Media Multi-Agent API",
    description="AI content generation using multi-agent pipelines with dynamic platform prompts",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One router now — clean and simple
app.include_router(content_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}