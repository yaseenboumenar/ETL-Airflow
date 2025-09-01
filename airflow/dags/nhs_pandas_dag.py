from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

READ_BUCKET  = Variable.get("READ_BUCKET_NAME",  default_var="nhs-etl-datasets")
WRITE_BUCKET = Variable.get("WRITE_BUCKET_NAME", default_var="nhs-etl-ingest-dev")

with DAG(
    dag_id="nhs_pandas_daily",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args={"owner": "airflow"},
) as dag:

    transform = BashOperator(
        task_id="transform",
        bash_command="python /opt/etl/scripts/transform_pandas.py",
        env={"READ_BUCKET_NAME": READ_BUCKET, "WRITE_BUCKET_NAME": WRITE_BUCKET},
    )

    load = BashOperator(
        task_id="load_postgres",
        bash_command="python /opt/etl/scripts/load_postgres.py",
        env={
            "BUCKET_NAME": WRITE_BUCKET,  # <- read silver from WRITE
            "DB_URL": "postgresql+psycopg2://etluser:etlpass@db:5432/etlwarehouse",
        },
    )

    transform >> load