from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    timestamp: str

class MLRequest(BaseModel):
    """
    Запрос от API сервиса
    """
    url: str
    request_id: str
    user_id: str

class PlantType(str, Enum):
    """Тип растения"""
    SHRUB = "Кустарник"
    TREE = "Дерево"


class Defect(BaseModel):
    """Дефект растения"""
    id: int = Field(..., ge=1, description="Уникальный идентификатор дефекта")
    name: str = Field(max_length=256)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Уверенность распознавания дефекта")


class Plant(BaseModel):
    """Схема растения"""
    id: int = Field(..., ge=1, description="Уникальный идентификатор растения")
    plant_type: PlantType = Field(..., description="Тип растения")
    name: str = Field(..., min_length=1, description="Название растения")
    latin_name: Optional[str] = Field(None, description="Латинское название растения")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Уверенность распознавания растения")
    defects: List[Defect] = Field(default_factory=list, description="Список дефектов растения")
    processing_time: float = Field(default=0.0, description="Время обработки")
    crop_url: str = Optional


class MLResponse(BaseModel):
    """Ответ ML-сервиса на запрос анализа изображения, такой же должен
    ожидать API сервис"""
    plants: List[Plant]

class Crop(BaseModel):
    id: int = Field(..., ge=1, description="Идентификатор кропа в пределах одной фотографии")
    crop_bytes: bytes
    url_image: str

trees_dict: List[Plant] = [
    Plant(id=1, name="Клен остролистный", latin_name="Acer platanoides", plant_type=PlantType.TREE),
    Plant(id=2, name="Лиственница", latin_name="Larix", plant_type=PlantType.TREE),
    Plant(id=3, name="Туя", latin_name="Thuja", plant_type=PlantType.TREE),
    Plant(id=4, name="Рябина", latin_name="Sorbus", plant_type=PlantType.TREE),
    Plant(id=5, name="Береза", latin_name="Betula", plant_type=PlantType.TREE),
    Plant(id=6, name="Каштан", latin_name="Castanea", plant_type=PlantType.TREE),
    Plant(id=7, name="Ива", latin_name="Salix", plant_type=PlantType.TREE),
    Plant(id=8, name="Клен ясенелистный", latin_name="Acer negundo", plant_type=PlantType.TREE),
    Plant(id=9, name="Осина", latin_name="Populus tremula", plant_type=PlantType.TREE),
    Plant(id=10, name="Липа", latin_name="Tilia", plant_type=PlantType.TREE),
    Plant(id=11, name="Ясень", latin_name="Fraxinus", plant_type=PlantType.TREE),
    Plant(id=12, name="Дуб", latin_name="Quercus", plant_type=PlantType.TREE),
    Plant(id=13, name="Ель", latin_name="Picea", plant_type=PlantType.TREE),
    Plant(id=14, name="Сосна", latin_name="Pinus", plant_type=PlantType.TREE),
    Plant(id=15, name="Вяз", latin_name="Ulmus", plant_type=PlantType.TREE),
    Plant(id=16, name="Сосна (кустарниковая форма)", latin_name="Pinus sylvestris f. fruticosa", plant_type=PlantType.SHRUB),
    Plant(id=17, name="Можжевельник", latin_name="Juniperus", plant_type=PlantType.SHRUB),
    Plant(id=18, name="Лапчатка кустарниковая (курильский чай)", latin_name="Pentaphylloides fruticosa", plant_type=PlantType.SHRUB),
    Plant(id=19, name="Чубушник", latin_name="Philadelphus", plant_type=PlantType.SHRUB),
    Plant(id=20, name="Сирень обыкновенная", latin_name="Syringa vulgaris", plant_type=PlantType.SHRUB),
    Plant(id=21, name="Карагана древовидная", latin_name="Caragana arborescens", plant_type=PlantType.SHRUB),
    Plant(id=22, name="Пузыреплодник калинолистный", latin_name="Physocarpus opulifolius", plant_type=PlantType.SHRUB),
    Plant(id=23, name="Спирея", latin_name="Spiraea", plant_type=PlantType.SHRUB),
    Plant(id=24, name="Кизильник", latin_name="Cotoneaster", plant_type=PlantType.SHRUB),
    Plant(id=25, name="Дерен белый", latin_name="Cornus alba", plant_type=PlantType.SHRUB),
    Plant(id=26, name="Лещина", latin_name="Corylus", plant_type=PlantType.SHRUB),
    Plant(id=27, name="Боярышник", latin_name="Crataegus", plant_type=PlantType.SHRUB),
    Plant(id=28, name="Роза собачья (шиповник)", latin_name="Rosa canina", plant_type=PlantType.SHRUB),
    Plant(id=29, name="Роза морщинистая", latin_name="Rosa rugosa", plant_type=PlantType.SHRUB)
]


defects: List[Defect] = [
    Defect(id=1, name="Комлевая гниль в сильной степени"),
    Defect(id=2, name="Стволовая гниль в сильной степени"),
    Defect(id=3, name="Обширная сухобочина"),
    Defect(id=4, name="Дупло"),
    Defect(id=5, name="Механические повреждения"),
    Defect(id=6, name="Отслоение коры"),
    Defect(id=7, name="Гниль плодовых тел"),
    Defect(id=8, name="Сухостой"),
    Defect(id=9, name="Повреждено вредителями"),
    Defect(id=10, name="Частичный вывал корневой системы"),
    Defect(id=11, name="Рак в сильной степени"),
    Defect(id=12, name="Пень"),
    Defect(id=13, name="Остолоп"),
    Defect(id=14, name="Сухобочина"),
    Defect(id=15, name="Глубокая продольная трещина"),
    Defect(id=16, name="Вывал корневой системы"),
    Defect(id=17, name="Сухие ветви более 75 %"),
    Defect(id=18, name="Сухие ветви от 50% до 75%"),
    Defect(id=19, name="Сухие ветви от 25 до 50%"),
    Defect(id=20, name="Сухие ветви до 25%"),
    Defect(id=22, name="Суховершинность"),
    Defect(id=23, name="Трещина"),
]
