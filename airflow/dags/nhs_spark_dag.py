# airflow/dags/nhs_spark_dag.py
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

READ_BUCKET  = Variable.get("READ_BUCKET_NAME",  default_var="nhs-etl-ingestion")
WRITE_BUCKET = Variable.get("WRITE_BUCKET_NAME", default_var="nhs-etl-dataset-silver")

with DAG(
    dag_id="nhs_spark_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "airflow"},
) as dag:

    transform = BashOperator(
        task_id="transform_spark",
        bash_command="python /opt/etl/scripts/transform_spark.py",
        env={
            "READ_BUCKET_NAME":  READ_BUCKET,
            "WRITE_BUCKET_NAME": WRITE_BUCKET,
        },
    )

    load = BashOperator(
        task_id="load_postgres",
        bash_command="python /opt/etl/scripts/load_postgres.py",
        env={
            "WRITE_BUCKET_NAME": WRITE_BUCKET,
            "DB_URL": "postgresql+psycopg2://etluser:etlpass@db:5432/etlwarehouse",
        },
    )

    transform >> load
