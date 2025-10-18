from enum import Enum
from typing import List, Optional, Dict

import cv2
import numpy as np
from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str
    timestamp: str

class ScanRequestSchema(BaseModel):
    request_id: str

class APIRequestSchema(BaseModel):
    """
    Запрос от API шлюза.
    """
    request_id: str
    user_id: str
    file: Optional[str] = None

    @model_validator(mode='after')
    def validate_image_file(self):
        if self.image_file:
            try:
                np_arr = np.frombuffer(self.image_file, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is None:
                    raise ValueError("Некорректные байты изображения")
            except Exception as e:
                raise ValueError(f"Некорректные байты изображения: {e}")
        return self


class ScanResponse(BaseModel):
    """
    Ответ ML-сервиса на запрос анализа изображения, такой же должен
    ожидать API сервис"""
    id: str = Field(description="ID сканирования")
    predict: "PredictSchema"



class DetectorSchema(BaseModel):
    crops: list["Crop"] = []
    framed_url: Optional[str] = Field(
        default=None,
        description="URL изображения с рамками"
    )


class PredictSchema(BaseModel):
    plants: List["Plant"]
    framed_url: Optional[str] = Field(description="Исходное фото с рамками")

class DefectSchema(BaseModel):
    """Дефект растения"""
    name: str = Field(max_length=256)
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Уверенность распознавания дефекта",
    )


class Plant(BaseModel):
    """Схема растения"""
    id: int = Field(..., ge=1, description="Уникальный идентификатор растения")
    name: str = Field(..., min_length=1, description="Название растения")
    latin_name: Optional[str] = Field(
        None,
        description="Латинское название растения",
    )
    type: str
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Уверенность распознавания растения",
    )
    defects: List["DefectSchema"] = Field(
        default_factory=list,
        description="Список дефектов растения",
    )
    processing_time: float = Field(default=0.0, description="Время обработки")
    crop_url: Optional[str] = Field(
        default=None,
        description="URL изображения. Может быть null"
    )



class Crop(BaseModel):
    id: int = Field(..., ge=0, description="Идентификатор кропа в пределах "
                                           "одной фотографии")
    crop_bytes: bytes
    url_image: str

class ClipReturnSchema(BaseModel):
    plant: "ClipPlantSchema"

class ClipPlantSchema(BaseModel):
    name: str
    latin_name: str
    confidence: float
    type: str
    defects: List = []
