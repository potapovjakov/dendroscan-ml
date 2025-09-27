from ultralytics import YOLO
import matplotlib.pyplot as plt
import cv2
import numpy as np

from settings import logger


class ObjectDetector:
    def __init__(self, weights_path: str):
        '''
        Класс для детекции и сегментации объектов с помощью YOLO.
        путь до весов модели (.pt файл)
        '''
        self.model = YOLO(weights_path)
        self.objects_info = []

    def predict(self, image_path: str, imgsz: int = 640, iou: float = 0.6, conf: float = 0.6, verbose: bool = True):
        '''
        Запуск инференса модели на изображении.
        путь до изображения
        '''
        self.image = cv2.imread(image_path)
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

    def show_results(self):
        '''
        Отображает изображение с разметкой.
        '''
        if not hasattr(self, "labeled_image"):
            logger.info("Нет результата для отображения. Сначала вызови predict().")
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


# Пример использования
if __name__ == '__main__':
    detector = ObjectDetector('../models/best.pt')
    detector.predict('-5382179392026965625_121.jpg')

    logger.info(f"Список ID объектов: {detector.get_object_ids()}")
    detector.show_results()