# scripts/load_postgres.py
import os, io
import boto3
import pyarrow.parquet as pq
import pandas as pd
from sqlalchemy import create_engine

# DAG will pass the WRITE bucket to this script under BUCKET_NAME
BUCKET     = os.getenv("BUCKET_NAME", "nhs-etl-ingest-dev")
SILVER_KEY = "silver/nhs_data/nhs_data.parquet"

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://etluser:etlpass@localhost:5432/etlwarehouse")

print(f"Reading s3://{BUCKET}/{SILVER_KEY}")
s3 = boto3.client("s3")
obj = s3.get_object(Bucket=BUCKET, Key=SILVER_KEY)
table = pq.read_table(io.BytesIO(obj["Body"].read()))
df = table.to_pandas()
print(f"✅ Read parquet shape={df.shape}")

engine = create_engine(DB_URL, future=True)
with engine.begin() as conn:
    print("✅ Connected to Postgres")
    df.to_sql("nhs_daily", con=conn, schema="public", if_exists="replace", index=False, method="multi", chunksize=1000)
    print(f"✅ Loaded {len(df):,} rows into public.nhs_daily")
