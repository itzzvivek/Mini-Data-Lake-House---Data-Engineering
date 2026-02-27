import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

MINIO_PORT=Minio("minio:9000", secure=False)
MINIO_HOST=os.getenv("MINIO_HOST")
MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME=os.getenv("MINIO_BUCKET_NAME")

minio_client = Minio(
    f"{MINIO_HOST}:{MINIO_PORT}",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

def ensure_bucket_exists(bucket_name):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    else:
        print(f"Bucket '{bucket_name}' already exists.")