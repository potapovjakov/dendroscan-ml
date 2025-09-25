from typing import List

from schemas.schemas import Plant, PlantType, Defect, Crop
from utils.files_utils import jpg_to_bytes
from utils.s3_util import upload_file


def get_predict(image_content: bytes, request_id: str) -> List[Plant]:
    """Главная ML функция."""

    crops = get_crops_img(image_content, request_id=request_id)
    plants = []
    for crop in crops:
        plant = get_plant_predict(crop.crop_bytes, crop.id)
        if plant:
            plants.append(plant)
            defect = get_defects_predict(crop)
            if defect:
                plant.defects = defect
    return plants

def get_crops_img(image_content: bytes, request_id) -> List[Crop]:
    """
    Функция должна принять исходное фото и вернуть список с кропами и id всех найденных растений.
    #Todo Пока возвражает захардкоженные кропы
    """
    crop_2_bytes = jpg_to_bytes("/app/temp_images/listvennica_crop.png")
    crop_22_bytes = jpg_to_bytes("/app/temp_images/kust_crop.png")
    #Todo Сделать выгрузку кропов в S3
    url_crop_2_url = upload_file(
        file_content=crop_2_bytes,
        filename="listvennica_crop.png",
        request_id=request_id
    )
    url_crop_22_url = upload_file(
        file_content=crop_22_bytes,
        filename="kust_crop.png",
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

    return [crop_2, crop_22]

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
