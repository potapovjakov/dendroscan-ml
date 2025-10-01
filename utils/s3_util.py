import asyncio
import uuid
from urllib.parse import urlparse

import aioboto3
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, ConnectTimeoutError, \
    ReadTimeoutError
from types_aiobotocore_s3.client import S3Client
from settings import (AWS_ACCESS_KEY_ID, AWS_REGION_NAME,
                      AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME, S3_ENDPOINT_URL,
                      logger, S3_PUBLIC_BUCKET)




aiosession = aioboto3.Session(
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    region_name=AWS_REGION_NAME,
)

# session = boto3.Session(
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
# )

# s3 = session.client(
#     service_name='s3',
#     endpoint_url=S3_ENDPOINT_URL,
#     config=boto3.session.Config(signature_version='s3v4'),
#     region_name=AWS_REGION_NAME
# )
#
# def download_file(file_url: str) -> bytes:
#     """
#     Скачивает файл из S3 и возвращает его содержимое в виде bytes
#
#     Args:
#         file_url (str): URL файла в S3
#
#     Returns:
#         bytes: Содержимое файла
#     """
#     try:
#         parsed_url = urlparse(file_url)
#         path_parts = parsed_url.path.lstrip('/').split('/')
#         key = path_parts[1]
#         response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
#         file_content = response['Body'].read()
#         return file_content
#
#     except ClientError as e:
#         error_code = e.response['Error']['Code']
#         if error_code == '404':
#             raise FileNotFoundError(f"Файл не найден в S3: {file_url}") from e
#         elif error_code == '403':
#             raise PermissionError(f"Нет доступа к файлу: {file_url}") from e
#         else:
#             raise Exception(f"Ошибка при скачивании файла: {e}") from e


# def upload_file(file_content: bytes, filename: str, request_id: uuid.UUID) -> str:
#     """
#     Загружает файл в S3 bucket
#
#     Args:
#         file_content: Содержимое файла в виде bytes
#         filename: Имя файла
#         request_id: ID запроса
#     Returns:
#         str: URL загруженного файла
#
#     Raises:
#         HTTPException: Если произошла ошибка при загрузке
#     """
#     s3_key = f"{request_id}/{filename}"
#     try:
#         s3.put_object(
#             Bucket=S3_BUCKET_NAME,
#             Key=s3_key,
#             Body=file_content,
#         )
#         file_url = f"{S3_PUBLIC_BUCKET}/{s3_key}"
#         logger.info(f"Файл успешно загружен в S3 как {file_url}")
#         return file_url
#
#     except ClientError as e:
#         error_msg = f"Ошибка при загрузке файла в S3: {e}"
#         logger.error(error_msg)
#         raise HTTPException(status_code=500, detail=error_msg)
#
#     except Exception as e:
#         error_msg = f"Неожиданная ошибка: {e}"
#         logger.error(error_msg)
#         raise HTTPException(status_code=500, detail=error_msg)


async def upload_file(
    filename: str,
    file_content: bytes,
    request_id: uuid.UUID,
) -> str:
    s3_key =  f"{request_id}/{filename}"

    config = Config(
        connect_timeout=5,
        read_timeout=30,
    )

    async with aiosession.client(
            "s3",
            endpoint_url=S3_ENDPOINT_URL,
            config=config,
    ) as s3:
        s3: S3Client
        try:
            logger.info(f"Uploading {s3_key} to s3")
            try:
                await s3.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=file_content,
                )
                logger.info(f"Finished Uploading {s3_key} to s3")
                file_url = f"{S3_PUBLIC_BUCKET}/{s3_key}"
                return file_url
            except asyncio.TimeoutError:
                logger.error(f"Upload operation timed out for {s3_key}")
                return "Изображение не было загружено (таймаут)"

        except (ConnectTimeoutError, ReadTimeoutError) as e:
            logger.error(f"S3 connection timeout: {e}")
            return "Изображение не было загружено (таймаут подключения)"
        except ClientError as e:
            logger.error(f"S3 client error: {e}")
            return "Изображение не было загружено (ошибка S3)"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "Изображение не было загружено"
