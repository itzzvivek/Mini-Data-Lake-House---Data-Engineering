from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import os
import requests
from dotenv import load_dotenv
from urllib.parse import unquote
from minio import Minio
from minio.credentials import StaticProvider
from config.minio_client import minio_client, ensure_bucket_exists

load_dotenv()

MINIO_PORT=os.getenv("MINIO_PORT")
MINIO_ROOT_USER=os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD=os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME=os.getenv("MINIO_BUCKET_NAME")

minio_client = Minio(
    MINIO_PORT.replace("http://", "").replace("https://", ""),
    credentials=StaticProvider(MINIO_ROOT_USER,MINIO_ROOT_PASSWORD),
    secure=False
)

BUCKET_NAME="mini-datalake"
RAW_FOLDER="raw-data"
PORCESSED_FOLDER="processed-data"


with DAG(
    dag_id="data_sources_dag",
    description="DAG to fetch data from external sources and store in MinIO",
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['data_sources'],
) as dag:
    
    def fetch_and_store_data():
        ensure_bucket_exists(BUCKET_NAME)
        data_source_url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(data_source_url)
        if response.status_code == 200:
            data = response.json()
            object_name = f"{RAW_FOLDER}/posts_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            minio_client.put_object(
                bucket_name=BUCKET_NAME,
                object_name=object_name,
                data=str(data).encode('utf-8'),
                length=len(str(data).encode('utf-8'))
            )
            print(f"Data stored in MinIO at {object_name}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")

    fetch_and_store_task = PythonOperator(
        task_id="fetch_and_store_data",
        python_callable=fetch_and_store_data
    )

    fetch_and_store_task