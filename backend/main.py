# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis import transcript_api, call_api
from config import loaded_config, ENVIRONMENT
from database import init_database

init_database()

config = loaded_config

app = FastAPI(
    title="GenAI-Powered Conversation Insights API",
    description="API for processing debt collection transcripts and generating insights.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # List of allowed origins for CORS
    # Adjust this to your frontend origin later on. Ex: "https://yourdomain.com"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include Transcript-level API endpoints
app.include_router(
    transcript_api.router,
    prefix=config.API_PREFIX + "/apis/transcripts",
    tags=["Transcripts"]
)

# Include Call-level API endpoints
app.include_router(
    call_api.router,
    prefix=config.API_PREFIX + "/apis/calls",
    tags=["Calls"]
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:backend", host="0.0.0.0", port=8000, reload=True)
