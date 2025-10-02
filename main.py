import uuid
from datetime import datetime
from typing import Optional, Annotated
from urllib.parse import urlparse

from fastapi import Body, Depends, FastAPI, Header, HTTPException, UploadFile, \
    Form
from fastapi.middleware.cors import CORSMiddleware

from schemas.schemas import HealthResponse, ScanResponse, APIRequestSchema, \
    ScanRequestSchema
from settings import ML_TOKEN, logger, S3_PUBLIC_BUCKET, S3_BUCKET_NAME
from utils.files_utils import get_image_bytes, check_file
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


@app.post("/scan", response_model=ScanResponse)
async def scan(
    file: UploadFile,
    request_id: str = Form(...),
    user_id: str = Form(...),
    token_verified: bool = Depends(verify_ml_token),
):

    logger.info(f"Получен новый запрос от API: {request_id}, ID пользователя: "
                f"{user_id}")
    scan_id = str(uuid.uuid4())
    logger.info(f"Начат процесс сканирования: {scan_id}")
    try:
        image_bytes = await file.read()
        predict = await get_predict(image_bytes, request_id)
        response = ScanResponse(
            id=scan_id,
            predict=predict,
        )
        logger.warning(f"ML RESPONSE: {response}")
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error {str(e)}")
