from typing import Any, Dict, List, Union

import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
from ultralytics import YOLO

from settings import INF_CONF, INF_IOU, logger
from utils.files_utils import get_image_bytes


class ObjectDetector:
    def __init__(self, weights_path: str):
        '''
        Класс для детекции и сегментации объектов с помощью YOLO.
        путь до весов модели (.pt файл)
        '''
        self.model = YOLO(weights_path)
        self.objects_info = []

    def predict(self, image_input: Union[str, bytes], imgsz: int = 640,
                iou: float = None, conf: float = None,
                verbose: bool =
                True):
        '''
        Запуск инференса модели на изображении.

        Args:
            image_input: путь до изображения или bytes изображения
            imgsz: размер изображения для модели
            iou: порог IoU
            conf: порог уверенности
            verbose: вывод информации о процессе
        '''
        # Проверка переменных INF_IOU и INF_CONF
        default_iou = getattr(self, INF_IOU, 0.6)
        default_conf = getattr(self, INF_CONF, 0.6)

        iou = iou if iou is not None else default_iou
        conf = conf if conf is not None else default_conf
        # Загрузка изображения в зависимости от типа входных данных

        if isinstance(image_input, str):
            # Вход - путь к файлу
            self.image = cv2.imread(image_input)
            if self.image is None:
                logger.error(f"Не удалось загрузить изображение по пути: {image_input}")
                return None
        elif isinstance(image_input, bytes):
            # Вход - bytes
            nparr = np.frombuffer(image_input, np.uint8)
            self.image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if self.image is None:
                logger.error("Не удалось декодировать изображение из bytes")
                return None
        else:
            logger.error("Неверный тип входных данных. Ожидается str (путь) или bytes")
            return None

        # Сохраняем оригинальные bytes для возможного повторного использования
        self.original_input = image_input

        results = self.model(self.image, imgsz=imgsz, iou=iou, conf=conf, verbose=verbose)
        self.res = results[0]

        if self.res.boxes is None or len(self.res.boxes) == 0:
            logger.info("Объекты не найдены")
            self.objects_info = []
            return None

        self._process_results()
        return self.objects_info

    def _process_results(self):
        '''
        Обрабатывает результаты инференса: боксы, маски, классы.
        '''
        classes = self.res.boxes.cls.cpu().numpy().astype(int)
        class_names = self.res.names
        boxes = self.res.boxes.xyxy.cpu().numpy().astype(int)
        masks = self.res.masks.data.cpu().numpy() if self.res.masks is not None else []

        labeled_image = self.image.copy()
        objects_info = []
        colors = [tuple(np.random.randint(0, 256, 3).tolist()) for _ in range(len(boxes))]

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = box
            class_id = int(classes[i])
            class_name = class_names[class_id]
            color = colors[i]

            # Наложение маски
            if len(masks) > 0:
                mask = masks[i]
                mask_resized = cv2.resize(mask, (self.image.shape[1], self.image.shape[0]),
                                          interpolation=cv2.INTER_NEAREST)

                mask_contours, _ = cv2.findContours(mask_resized.astype(np.uint8),
                                                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                overlay = labeled_image.copy()
                cv2.drawContours(overlay, mask_contours, -1, color, thickness=-1)
                alpha = 0.4
                labeled_image = cv2.addWeighted(overlay, alpha, labeled_image, 1 - alpha, 0)

                cv2.drawContours(labeled_image, mask_contours, -1, color, 2)

            # Bounding box
            cv2.rectangle(labeled_image, (x1, y1), (x2, y2), color, 2)

            # Подпись
            label = f"id={i}, {class_name}"
            cv2.putText(labeled_image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Сохраняем инфу
            objects_info.append({
                "id": i,
                "class_id": class_id,
                "class_name": class_name,
                "bbox": box.tolist()
            })

        self.labeled_image = labeled_image
        self.objects_info = objects_info

    def get_objects_with_crops(self, image_format: str = 'jpg', quality: int = 95) -> List[Dict[str, Any]]:
        '''
        Возвращает список найденных объектов с обрезанными изображениями в формате bytes.

        Args:
            image_format: формат изображения ('jpg', 'png')
            quality: качество для JPEG (0-100)

        Returns:
            List[Dict]: список объектов с id, img_crop_bytes и class_id
        '''
        if not hasattr(self, "objects_info") or not self.objects_info:
            logger.error("Нет результатов детекции. Сначала вызовите predict("
                        ").")
            return []

        if not hasattr(self, "image") or self.image is None:
            logger.error("Исходное изображение не найдено.")
            return []

        objects_with_crops = []

        for obj in self.objects_info:
            # Получаем координаты bounding box
            x1, y1, x2, y2 = obj["bbox"]

            # Обрезаем изображение по bounding box
            crop = self.image[y1:y2, x1:x2]

            # Проверяем, что обрезанная область не пустая
            if crop.size == 0:
                logger.warning(f"Пустая область для объекта {obj['id']}")
                continue

            # Кодируем обрезанное изображение в bytes
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality] if image_format.lower() == 'jpg' else []

            if image_format.lower() in ['jpg', 'jpeg']:
                success, encoded_image = cv2.imencode('.jpg', crop, encode_param)
            elif image_format.lower() == 'png':
                success, encoded_image = cv2.imencode('.png', crop)
            else:
                logger.error(f"Неподдерживаемый формат: {image_format}")
                success = False

            if success:
                img_bytes = encoded_image.tobytes()

                objects_with_crops.append({
                    "id": obj["id"],
                    "img_crop_bytes": img_bytes,
                    "class_id": obj["class_id"],
                    "class_name": obj.get("class_name", ""),
                    "bbox": obj["bbox"]
                })
            else:
                logger.error(f"Ошибка кодирования изображения для объекта {obj['id']}")

        return objects_with_crops

    def show_results(self):
        '''
        Отображает изображение с разметкой.
        '''
        if not hasattr(self, "labeled_image"):
            logger.error("Нет результата для отображения. Сначала вызови "
                     "predict().")
            return

        plt.figure(figsize=(8, 8), dpi=150)
        image_rgb = cv2.cvtColor(self.labeled_image, cv2.COLOR_BGR2RGB)
        plt.imshow(image_rgb)
        plt.axis("off")
        plt.show()

    def get_object_ids(self):
        '''
        Возвращает список ID найденных объектов.
        '''
        return [obj["id"] for obj in self.objects_info]

    def get_annotated_image_bytes(self, image_format: str = 'jpg', quality: int = 95) -> bytes:
        """
        Возвращает размеченное изображение с bounding boxes в формате bytes.
        Если пришёл PNG, конвертирует в JPEG на лету (через PyTorch/NumPy, без PIL).

        Args:
            image_format: формат исходного изображения ('jpg' или 'png')
            quality: качество для JPEG (0-100)

        Returns:
            bytes: размеченное изображение в формате JPEG
        """
        if not hasattr(self, "labeled_image"):
            logger.error("Нет результата для кодирования. Сначала вызовите "
                     "predict().")
            return b''

        img = self.labeled_image  # numpy array, BGR

        # Если PNG, перекодируем в JPEG
        if image_format.lower() == 'png':
            # Конвертируем в torch tensor
            img_tensor = torch.from_numpy(img)  # HWC, BGR
            img_tensor = img_tensor.permute(2, 0, 1).contiguous()  # CHW

            # Можно дополнительно сконвертировать в RGB, если нужно
            img_tensor = img_tensor[[2, 1, 0], :, :]  # BGR -> RGB

            # Конвертируем обратно в numpy для OpenCV JPEG кодирования
            img = img_tensor.permute(1, 2, 0).cpu().numpy()  # HWC, RGB
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # RGB -> BGR для JPEG

        # Кодируем в JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, encoded_image = cv2.imencode('.jpg', img, encode_param)

        if success:
            return encoded_image.tobytes()
        else:
            logger.error("Ошибка кодирования размеченного изображения")
            return b''

def test_predict():
    detect = ObjectDetector("../models/best.pt")
    img_bytes = get_image_bytes("https://dendroscan.s3.cloud.ru/test_image.jpeg")
    detect.predict(image_input=img_bytes)
    objects = detect.get_objects_with_crops()
    assert len(objects) > 1
    for obj in objects:
        required_keys = {'id', 'img_crop_bytes', 'class_id', 'class_name', 'bbox'}
        assert required_keys.issubset(obj.keys()), f"Отсутствуют ключи: {
        required_keys - set(obj.keys())}"
        assert type(obj["img_crop_bytes"]) == bytes
        assert type(obj["class_id"]) == int
        assert type(obj["class_name"]) == str
        assert type(obj["bbox"]) == list

# Пример использования
if __name__ == '__main__':
    test_predict()



    # detector = ObjectDetector('../models/best.pt')
    #
    # # Загрузка из файла
    # detector.predict('test_image.jpeg')
    # logger.info(f"Список ID объектов: {detector.get_object_ids()}")
    #
    # # Загрузка из bytes
    # with open('test_image.jpeg', 'rb') as f:
    #     image_bytes = f.read()
    #
    # detector.predict(image_bytes)
    # objects_with_crops = detector.get_objects_with_crops()
    # logger.info(f"Найдено объектов с кропами: {len(objects_with_crops)}")
    # # Сохранение кропов в файлы
    # for obj in objects_with_crops:
    #     with open(f"object_{obj['id']}_{obj['class_name']}.jpg", "wb") as f:
    #         f.write(obj['img_crop_bytes'])
    #     logger.info(f"Сохранен объект {obj['id']}: {obj['class_name']}")
    #
    # # Получение размеченного изображения в bytes
    # annotated_image_bytes = detector.get_annotated_image_bytes()
    # with open("annotated_image.jpg", "wb") as f:
    #     f.write(annotated_image_bytes)
    #
    # detector.show_results()
