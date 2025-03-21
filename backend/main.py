# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apis import register_routes
from config import loaded_config
from database import init_database

config = loaded_config

app = FastAPI(
    title="GenAI-Powered Conversation Insights API",
    description="API for processing debt collection transcripts and generating insights.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # List of allowed origins for CORS
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

init_database()
register_routes(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:backend", host="0.0.0.0", port=8000, reload=True)
