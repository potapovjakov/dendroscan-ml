import requests
import logging

from fastapi import HTTPException
from requests.exceptions import Timeout, RequestException, HTTPError

from fastapi import HTTPException, UploadFile, File

from settings import MAX_FILE_SIZE


def check_file(file: UploadFile = File(...)) -> UploadFile:
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только изображения"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Файл пустой")

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимум {MAX_FILE_SIZE} байт"
        )

    file.file.seek(0)
    return file


def get_image_bytes(url):
    try:
        response = requests.get(
            url,
            timeout=30,
        )
        response.raise_for_status()
        logging.info(f"Получил ответ {response}")
        image_bytes = response.content
        return image_bytes

    except Timeout:
        logging.error(f"Таймаут при попытке получить изображение по URL: {url}")
        raise HTTPException(status_code=408, detail=f"Timeout while fetching image from {url}")

    except HTTPError as e:
        status_code = e.response.status_code
        logging.error(f"HTTP ошибка при получении изображения: {status_code} - {url}")
        if status_code == 404:
            raise HTTPException(status_code=404, detail=f"Image not found at {url}")
        elif status_code == 403:
            raise HTTPException(status_code=403, detail=f"Access forbidden to {url}")
        else:
            raise HTTPException(status_code=status_code, detail=f"HTTP error {status_code} while fetching image from {url}")

    except RequestException as e:
        logging.error(f"Ошибка сети при получении изображения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Network error while fetching image from {url}")

    except Exception as e:
        logging.error(f"Неожиданная ошибка при получении изображения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error while fetching image from {url}")
