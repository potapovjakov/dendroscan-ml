import logging

import requests

def get_image_bytes(url):
    """
    Функция для скачивания картинок с публичного бакета
    :param url:
    :return:
    """
    try:
        logging.info(f"Пытаюсь загрузить файл по урл: {url}")
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Получил ответ {response}")
        image_bytes = response.content
        return image_bytes

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке: {e}")
        return None
