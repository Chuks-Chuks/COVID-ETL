from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
import pandas as pd
from extract_class import CovidExtractor

# Creating function to return Covid data

def _return_covid_data():
	"""
	This function returns the COVID data from the extract class
	"""
	extract = CovidExtractor()
	return extract.extract_covid_information()

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
	# Adding the extract task to fetch all historical covid data
	extract_task = PythonOperator(
		task_id='extract_historical_data',
		python_callable=_return_covid_data
	)
