import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

MINIO_HOST=os.getenv("MINIO_HOST")
MINIO_PORT=os.getenv("MINIO_PORT")
MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME=os.getenv("MINIO_BUCKET_NAME")

client = Minio(
    f"{MINIO_HOST}:{MINIO_PORT}",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

def ensuer_bucket_exists(bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)