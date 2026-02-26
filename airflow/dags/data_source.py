from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import unquote
from minio import Minio
from minio.credentials import StaticProvider
from ../config.minio_client import minio_client, ensure_bucket_exists

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

today = datetime.utcnow().strftime("%Y-%m-%d")

##=== minio write function ===##
def upload_to_minio(source_name, data):
    file_path = f"/tmp/{source_name}_{today}.json"

    with open(file_path, "w") as f:
        json.dump(data, f)

    ensure_bucket_exists(BUCKET_NAME)

    minio_client.fput_object(
        BUCKET_NAME,
        f"{RAW_FOLDER}/{source_name}/{today}.json",
        file_path
    )

    os.remove(file_path)

# get raw data from apis

CITIES = {
        "Delhi": {"lat": 28.7041, "lon": 77.1025},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Tokyo": {"lat": 35.6895, "lon": 139.6917},
        "Sydney": {"lat": -33.8688, "lon": 151.2093}
    }

def fetch_weather(city, lat, lon):
    url = ( f"https://api.openmeteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation_sum&current_weather=true&timezone=auto" )
    response = requests.get(url)
    upload_to_minio(f"weather_{city}", response.json())

def fetch_news():
    NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
    url = f" https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q=all"
    response = requests.get(url)
    upload_to_minio("news", response.json())

def fetch_crypto():
    CRYPTO_API_KEY = os.getenv("COINGECKO_API")
    headers = {"X-CoinAPI-Key": CRYPTO_API_KEY, "Accept": "application/json"}
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1
    }
    response = requests.get(url,headers=headers, params=params)
    upload_to_minio("crypto", response.json())

def fetch_countries():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    upload_to_minio("countries", response.json())


#=== DAG Definition ===##

default_args = {
    'owner': 'vivek',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='data_sources_dag',
    default_args=default_args,
    description='DAG to fetch data from various APIs and store in MinIO',
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data_sources', 'minio']
) as dags:
    
    weather_tasks = PythonOperator(
        task_id=f'fetch_weather',
        python_callable = fetch_weather
    )

    news_task = PythonOperator(
        task_id='fetch_news',
        python_callable=fetch_news
    )

    crypto_task = PythonOperator(
        task_id='fetch_crypto',
        python_callable=fetch_crypto
    )

    countries_task = PythonOperator(
        task_id='fetch_countries',
        python_callable=fetch_countries
    )


    # Run in parallel

    [weather_tasks,news_task, crypto_task, countries_task]