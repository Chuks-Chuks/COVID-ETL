from airflow import DAG 
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

def test_postgres():
    try:
        # Testing the connection
        hook = PostgresHook(postgres_conn_id='postgres_covid_conn')
        conn = hook.get_conn()
        cursor = conn.cursor()  # Testing the query execution
        cursor.execute('SELECT 1;')
        result = cursor.fetchone()

        if result and result[0] == 1:
            return "connection validated"
        else:
            raise ValueError(f'unexpected query result: {result}')
        print(result)
    except Exception as e:
        print(f"Connection test failed: {str(e)}", file=sys.stderr)
        raise
    finally:
        if 'conn' in locals():
            conn.close()


with DAG(
    'test_db_connection', 
    start_date=datetime(2023, 1, 1), 
    schedule=None ,catchup=False,
    default_args={
        'retries':1,
        'retry_delay': timedelta(minutes=1)
    }
    ) as dag:
    test_task = PythonOperator(
        task_id = 'test_connection',
        python_callable=test_postgres, 
        do_xcom_push=True
    )