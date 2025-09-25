import time
import uuid
from typing import List

from schemas.schemas import Plant, PlantType, Defect, Crop


def get_predict(image_content: bytes, request_id: uuid.UUID) -> List[Plant]:
    """Главная ML функция."""
    pass

def get_classes_img(image_content: bytes) -> List[Crop]:
    """
    Функция должна принять исходное фото и вернуть список с кропами всех найденных растений.
    """
    pass


def  get_plant_predict(crop_image: bytes) -> List[Plant]:
    """
    Функция для получения предсказания породы растения на основе файла с изображением.
    """
    start_time = time.time()

    plant_1 = Plant(id=2, name="Лиственница", latin_name="Larix", plant_type=PlantType.TREE)
    plant_2 = Plant(id=22, name="Пузыреплодник калинолистный", latin_name="Physocarpus opulifolius", plant_type=PlantType.SHRUB)
    defect_list = []
    defect = get_defects_predict(crop_image)
    processing_time = time.time() - start_time


def get_defects_predict(crop_image) -> Defect:
    defect = Defect(id=17, name="Сухие ветви более 75 %")
    return defect
