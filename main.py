import os
import time
from datetime import datetime
from urllib.parse import urlparse

from fastapi import HTTPException, Header, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from settings import ML_TOKEN
from PIL import Image
from typing import Optional

from pydantic import BaseModel

from s3_util import download_file

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

class MLResponse(BaseModel):
    type: str
    file_type: str
    width: float
    height: float
    file_size: float
    trunk_root: bool
    hollow: bool
    crack: bool
    processing_time: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str


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
    url: str,
    token_verified: bool = Depends(verify_ml_token)
):
    start_time = time.time()
    try:
        if not url.startswith("http"):
            raise HTTPException(status_code=400, detail="Invalid MinIO URL format")
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.lstrip('/').split('/')
        if len(path_parts) < 2:
            raise HTTPException(status_code=400, detail="Invalid MinIO URL format")

        key = '/'.join(path_parts[1:])

        file_content = download_file(url)
        file_size = len(file_content)
        file_extension = os.path.splitext(key)[1].lower().replace('.', '')

        width, height = 0, 0
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
            try:
                # Создаем временный файл в памяти с помощью BytesIO
                from io import BytesIO
                image_stream = BytesIO(file_content)
                with Image.open(image_stream) as img:
                    width, height = img.size
                    if img.format:
                        file_extension = img.format.lower()
            except Exception as img_error:
                raise HTTPException(status_code=400, detail=f"Invalid image file: {str(img_error)}")
            processing_time = time.time() - start_time  # Конец замера времени

            return MLResponse(
                type="chestnut",
                trunk_root=True,
                hollow=False,
                crack=True,
                file_type=file_extension,
                width=width,
                height=height,
                file_size=file_size,
                processing_time=round(processing_time, 4),
            )
        else:
            raise HTTPException(status_code=400, detail="Images only")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
