import logging
import os
import sys

from dotenv import load_dotenv

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%('
               'lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PUBLIC_BUCKET = os.getenv("S3_PUBLIC_BUCKET")
ML_TOKEN = os.getenv("ML_TOKEN")

# Параметры ML инференса:
INF_MODEL_PATH = os.getenv("INF_MODEL_PATH", "../models/best.pt")
INF_IOU = os.getenv("INF_IOU", 0.6)
INF_CONF = os.getenv("INF_CONF", 0.6)
