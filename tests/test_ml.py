from utils.files_utils import get_image_bytes
from segmentator.segmentator_inferense import ObjectDetector

def test_predict():
    detect = ObjectDetector()
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
