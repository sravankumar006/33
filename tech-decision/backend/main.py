import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router
from app.api.routers.phones import router as phones_router
from app.api.routers.discovery import router as discovery_router
from app.core.config import settings

app = FastAPI(title='Tech Decision API', version='0.1.0')

import logging
from fastapi import Request

logger = logging.getLogger("uvicorn.error")

frontend_origin = str(settings.frontend_url).rstrip('/') if settings.frontend_url else 'http://localhost:3000'
origins = [frontend_origin, 'http://localhost:3000', 'http://127.0.0.1:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code} for {request.method} {request.url.path}")
    return response

app.include_router(health_router)
app.include_router(phones_router)
app.include_router(discovery_router)

