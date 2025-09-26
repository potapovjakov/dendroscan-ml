import uuid
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas.schemas import HealthResponse, MLResponse, MLRequest
from settings import ML_TOKEN, logger
from utils.files_utils import get_image_bytes
from utils.predict_util import get_predict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://dendroscan.ru",
        "https://dendroscan.ru",
        "http://www.dendroscan.ru",
        "https://www.dendroscan.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


def verify_ml_token(ml_token: Optional[str] = Header(None)):
    """Проверка ML токена"""
    if not ml_token or ml_token != ML_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing ML token")
    return True

@app.post("/scan", response_model=MLResponse)
async def start(
    request_data: MLRequest = Body(...),
    token_verified: bool = Depends(verify_ml_token)
):
    request_id = request_data.request_id
    logger.info(f"Получен новый запрос {request_id}")
    # url = request_data.url ToDo Временно хардкодим
    url = "https://dendroscan.s3.cloud.ru/777a84e2-3523-47fd-8e88-21517f12428d/listv%2Bkust.jpeg"
    user_id = request_data.user_id
    # ml_request_id = uuid.uuid4() ToDo так же харкодим временно
    ml_request_id = uuid.UUID("666a84e2-3523-47fd-8e88-21517f12428d")

    try:
        if not url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid S3 URL format")
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.lstrip('/').split('/')
        if len(path_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid S3 URL format")

        img_bytes = get_image_bytes(url)

        plants = get_predict(img_bytes, request_id)

        if plants:
            return MLResponse(
                plants=plants,
            )


    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
