
def jpg_to_bytes(file_path: str) -> bytes:
    """
    Читает JPG файл и возвращает его содержимое в виде байтов.

    Args:
        file_path (str): Путь к JPG файлу

    Returns:
        bytes: Содержимое файла в виде байтов

    Raises:
        FileNotFoundError: Если файл не существует
        IOError: Если произошла ошибка при чтении файла
    """
    try:
        with open(file_path, 'rb') as file:
            image_content = file.read()
        return image_content
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл {file_path} не найден")
    except Exception as e:
        raise IOError(f"Ошибка при чтении файла: {e}")