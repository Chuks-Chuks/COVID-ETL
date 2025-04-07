from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import pandas as pd
import requests 

default_args = {
	'owner': 'philip',
	'retries': 1,
	'retry_delay': timedelta(minutes=5)
}

with DAG(
	'covid_etl_pipeline',
	default_args=default_args,
	start_date=datetime(2023, 1, 1),
	schedule_interval='@daily',
) as dag:
	pass
