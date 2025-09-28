import random
from typing import List

from schemas.schemas import (
    Plant,
    PlantType,
    Defect,
    Crop,
    PredictSchema,
    DetectorSchema, trees_dict, defects,
)
from utils.inst_segm_model_inf import ObjectDetector
from utils.s3_util import upload_file
from settings import logger, INF_MODEL_PATH


def get_predict(image_content: bytes, request_id: str) -> PredictSchema:
    """Главная ML функция."""
    detect = detect_plants(image_content, request_id=request_id)
    crops = detect.crops
    plants = []
    for crop in crops:
        plant = get_plant_predict(crop.crop_bytes)
        if plant:
            plant.crop_url = crop.url_image
            plants.append(plant)
            defect = get_defects_predict(crop.crop_bytes)
            plant.defects = defect
    predict_response = PredictSchema(
        plants=plants,
        framed_url=detect.framed_url,
    )
    return predict_response

def detect_plants(image_content: bytes, request_id) -> DetectorSchema:
    """
    Функция должна принять исходное фото и вернуть список с кропами, id всех
    найденных растений и фото с рамками найденных растений.
    #Todo Пока возвражает захардкоженные кропы, уже загруженные в S3 по request_id
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
        annotated_url = upload_file(
            file_content=annotated_image_bytes,
            filename=f"{request_id}_annotated.jpg",
            request_id=request_id
            )
        crops = []
        for obj in objects:
            url = upload_file(
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

def  get_plant_predict(crop_bytes: bytes) -> Plant | None:
    """
    Функция для получения предсказания породы растения на основе кропа растения.
    ToDo Пока возвращает random из коллекции schemas.trees_dict
    """
    return random.choice(trees_dict)


def get_defects_predict(crop_image: bytes) -> List[Defect] | []:
    """
    Функция поиска дефектов на кропе. ToDo пока возвращает хардкод

    :param crop_image: bytes
    :return: Всегда список. Даже если он пустой
    """
    count = random.randint(1, min(5, len(defects)))
    return random.sample(defects, count)
