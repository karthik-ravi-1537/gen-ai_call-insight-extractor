# apis/__init__.py

from apis.call_api import router as call_router
from apis.transcript_api import router as transcript_router
from config import loaded_config, ENVIRONMENT
from fastapi import FastAPI


def register_routes(app: FastAPI):
    config = loaded_config

    # Include Transcript-level API endpoints
    app.include_router(
        transcript_router,
        prefix=config.API_PREFIX + "/apis/transcripts",
        tags=["Transcripts"]
    )

    # Include Call-level API endpoints
    app.include_router(
        call_router,
        prefix=config.API_PREFIX + "/apis/calls",
        tags=["Calls"]
    )

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "environment": ENVIRONMENT}
