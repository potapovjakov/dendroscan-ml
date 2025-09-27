from typing import List

from schemas.schemas import (
    Plant,
    PlantType,
    Defect,
    Crop,
    PredictSchema,
    DetectorSchema,
)
from utils.files_utils import get_image_bytes
from utils.s3_util import upload_file
from settings import S3_PUBLIC_BUCKET, logger


def get_predict(image_content: bytes, request_id: str) -> PredictSchema:
    """Главная ML функция."""
    detect = detect_plants(image_content, request_id=request_id)
    crops = detect.crops
    plants = []
    for crop in crops:
        plant = get_plant_predict(crop.crop_bytes, crop.id)
        if plant:
            plant.crop_url = crop.url_image
            plants.append(plant)
            defect = get_defects_predict(crop.crop_bytes)
            plant.defects = defect
    predict_response = PredictSchema(
        plants=plants,
        framed_url=detect.framed_url,
    )
    logger.info(predict_response)
    return predict_response

def detect_plants(image_content: bytes, request_id) -> DetectorSchema:
    """
    Функция должна принять исходное фото и вернуть список с кропами, id всех
    найденных растений и фото с рамками найденных растений.
    #Todo Пока возвражает захардкоженные кропы, уже загруженные в S3 по request_id
    """
    logger.info("Попытка найти растения")
    crop_2_bytes = get_image_bytes(
        f"{S3_PUBLIC_BUCKET}/777a84e2-3523-47fd-8e88-21517f12428d/listvennica_crop.png")
    crop_22_bytes = get_image_bytes(
        f"{S3_PUBLIC_BUCKET}/777a84e2-3523-47fd-8e88-21517f12428d/kust_crop.png")
    framed_img_bytes = get_image_bytes(
        f"{S3_PUBLIC_BUCKET}/777a84e2-3523-47fd-8e88-21517f12428d/framed_image.jpeg")

    url_crop_2_url = upload_file(
        file_content=crop_2_bytes,
        filename="listvennica_crop.png",
        request_id=request_id,
    )
    url_crop_22_url = upload_file(
        file_content=crop_22_bytes,
        filename="kust_crop.png",
        request_id=request_id
    )
    framed_img_url = upload_file(
        file_content=framed_img_bytes,
        filename="framed_image.jpeg",
        request_id=request_id
    )
    crop_2 = Crop(
        id=2,
        crop_bytes=crop_2_bytes,
        url_image=url_crop_2_url,
    )
    crop_22 = Crop(
        id=22,
        crop_bytes=crop_22_bytes,
        url_image=url_crop_22_url,
    )

    plants = DetectorSchema(
        crops = [crop_2, crop_22],
        framed_url=framed_img_url,
    )
    logger.info(f"Найдено {len(plants.crops)} растения.")
    return plants


def  get_plant_predict(crop_bytes: bytes, plant_id: int) -> Plant | None: #Todo plant_id убрать после готовности мл функций
    """
    Функция для получения предсказания породы растения на основе кропа растения.
    ToDo Пока возвращает только 2 захардкоженных растения
    """
    if plant_id == 2:
        return Plant(id=2, name="Лиственница", latin_name="Larix", plant_type=PlantType.TREE)
    if plant_id == 22:
        return Plant(id=22, name="Пузыреплодник калинолистный", latin_name="Physocarpus opulifolius", plant_type=PlantType.SHRUB)
    return None


def get_defects_predict(crop_image: bytes) -> List[Defect] | []:
    """
    Функция поиска дефектов на кропе. ToDo пока возвращает хардкод

    :param crop_image: bytes
    :return: Всегда список. Даже если он пустой
    """
    defect = Defect(id=17, name="Сухие ветви более 75 %")
    return [defect]
