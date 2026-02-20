from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import os
import requests
from dotenv import load_dotenv
from urllib.parse import unquote
from minio import Minio
from minio.credentials import StaticProvider

load_dotenv()

MINIO_PORT=os.getenv("MINIO_PORT")
MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME=os.getenv("MINIO_BUCKET_NAME")

minio_client = Minio(
    f"localhost:{MINIO_PORT}",
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)