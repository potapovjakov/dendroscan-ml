import time
import uuid
from typing import List

from schemas.schemas import Plant, PlantType, Defect, Crop
from utils.files_utils import jpg_to_bytes


def get_predict(image_content: bytes, request_id: uuid.UUID) -> List[Plant]:
    """Главная ML функция."""

    crops = get_crops_img(image_content)
    plants = []
    for crop in crops:
        plant = get_plant_predict(crop.crop_bytes, crop.id)
        if plant:
            plants.append(plant)
            defect_list = []
            defect = get_defects_predict(crop)
            if defect:
                defect_list.append(defect)
                plant.defects = defect_list
    return plants

def get_crops_img(image_content: bytes) -> List[Crop]:
    """
    Функция должна принять исходное фото и вернуть список с кропами и id всех найденных растений.
    #Todo Пока возвражает захардкоженные кропы
    """
    crop_2_bytes = jpg_to_bytes("test_images/listvennica_crop.png")
    crop_22_bytes = jpg_to_bytes("test_images/kust_crop.png")
    #Todo Сделать выгрузку кропов в S3

    crop_1 = Crop(
        id=2,
        crop_bytes=crop_2_bytes,
    )
    crop_2 = Crop(
        id=22,
        crop_bytes=crop_22_bytes,
    )
    return [crop_1, crop_2]

def  get_plant_predict(crop_bytes: bytes, plant_id: int) -> Plant | None: #Todo plant_id убрать после готовности мл функций
    """
    Функция для получения предсказания породы растения на основе кропа растения.
    ToDo Пока возвращает только 2 захардкоженных растения
    """
    if plant_id == 1:
        return Plant(id=2, name="Лиственница", latin_name="Larix", plant_type=PlantType.TREE)
    if plant_id == 22:
        return Plant(id=22, name="Пузыреплодник калинолистный", latin_name="Physocarpus opulifolius", plant_type=PlantType.SHRUB)
    return None


def get_defects_predict(crop_image) -> List[Defect]:
    defect = Defect(id=17, name="Сухие ветви более 75 %")
    return [defect]
