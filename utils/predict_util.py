import time

from fastapi import HTTPException

from clip.clip_inferense import get_clip_predict
from schemas.schemas import (
    Plant,
    Crop,
    PredictSchema,
    DetectorSchema,
)
from segmentator.segmentator_inferense import ObjectDetector
from utils.s3_util import upload_file
from settings import logger


async def get_predict(image_content: bytes, request_id: str) -> PredictSchema:
    """Главная ML функция."""
    detect = await detect_plants(image_content, request_id=request_id)
    crops = detect.crops
    logger.info(f"Нашел {len(crops)} растений, отправляю на определение.")
    plants = []
    for crop in crops:
        plant = await get_plant_predict(crop.crop_bytes)
        if plant:
            plant.crop_url = crop.url_image
            plants.append(plant)
    predict_response = PredictSchema(
        plants=plants,
        framed_url=detect.framed_url,
    )
    return predict_response

async def detect_plants(image_content: bytes, request_id) -> DetectorSchema:
    """
    Функция должна принять исходное фото и вернуть список с кропами, id всех
    найденных растений и фото с рамками найденных растений.
    """
    logger.info("Попытка найти растения")
    detector = ObjectDetector()
    detector.predict(
        image_input=image_content,
    )

    objects = detector.get_objects_with_crops()
    logger.info(f"Найдено {len(objects)} растений.")
    if objects and len(objects) > 0:
        annotated_image_bytes = detector.get_annotated_image_bytes()
        annotated_url = await upload_file(
            file_content=annotated_image_bytes,
            filename=f"{request_id}_annotated.jpg",
            request_id=request_id
            )
        crops = []
        for obj in objects:
            url = await upload_file(
            file_content=obj["img_crop_bytes"],
            filename=f"object_{obj['id']}_{obj['class_name']}.jpg",
            request_id=request_id
            )
            crop = Crop(
            id=obj["id"],
            crop_bytes=obj["img_crop_bytes"],
            url_image=url,
            )
            crops.append(crop)
        plants = DetectorSchema(
            crops=crops,
            framed_url=annotated_url,
        )
        return plants
    else:
        return DetectorSchema(
            crops=[],
            framed_url=None,
        )

async def  get_plant_predict(crop_bytes: bytes) -> Plant | None:
    """
    Функция для получения предсказания породы растения на основе кропа растения.
    ToDo Пока возвращает random из коллекции schemas.trees_dict
    """
    logger.info(f"Начинаю классифицировать растение и его дефекты")
    start_time = time.time()
    try:
        result = get_clip_predict(crop_bytes)
        logger.info(f"result get plant predict: {result}")
        result_time = time.time() - start_time
        if len(result["plant"]) >= 0:
            logger.info(
                f"Определил растение как: {result['plant']['name']} за {result_time:.3f} сек."
            )
            logger.info(result)
            plant = Plant(
                id=1,
                name=result["plant"]["name"],
                latin_name=result["plant"]["latin_name"],
                confidence=result["plant"]["confidence"],
                type=result["plant"]["type"],
                defects=result["plant"]["defects"],
                processing_time=float(f"{result_time:.3f}"),
            )
            return plant
        return None
    except Exception as e:
        raise HTTPException(500, e)
