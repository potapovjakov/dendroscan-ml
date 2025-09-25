from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

from settings import (AWS_ACCESS_KEY_ID, AWS_REGION_NAME,
                      AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, S3_ENDPOINT_URL)

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

s3 = session.client(
    service_name='s3',
    endpoint_url=S3_ENDPOINT_URL,
    config=boto3.session.Config(signature_version='s3v4'),
    region_name=AWS_REGION_NAME
)

def download_file(file_url: str) -> bytes:
    """
    Скачивает файл из S3 и возвращает его содержимое в виде bytes

    Args:
        file_url (str): URL файла в S3

    Returns:
        bytes: Содержимое файла
    """
    try:
        parsed_url = urlparse(file_url)
        path_parts = parsed_url.path.lstrip('/').split('/')
        key = path_parts[1]
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        file_content = response['Body'].read()
        return file_content

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise FileNotFoundError(f"Файл не найден в S3: {file_url}") from e
        elif error_code == '403':
            raise PermissionError(f"Нет доступа к файлу: {file_url}") from e
        else:
            raise Exception(f"Ошибка при скачивании файла: {e}") from e
