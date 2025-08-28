# scripts/load_postgres.py
import os, io, boto3, pyarrow.parquet as pq
import pandas as pd
from sqlalchemy import create_engine

BUCKET = (os.getenv("BUCKET_NAME", "nhs-etl-datasets"))
SILVER_KEY = "silver/nhs_data/nhs_data.parquet"

# Use DB_URL env var if provided (Airflow), else localhost (your laptop)
DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://etluser:etlpass@localhost:5432/etlwarehouse"
)

s3 = boto3.client("s3")
obj = s3.get_object(Bucket=BUCKET, Key=SILVER_KEY)
table = pq.read_table(io.BytesIO(obj["Body"].read()))
df = table.to_pandas()
print(f"✅ Read parquet shape={df.shape}")

engine = create_engine(DB_URL, future=True)
with engine.begin() as conn:
    print("✅ Connected to Postgres")

df.to_sql("nhs_daily", con=engine, schema="public",
          if_exists="replace", index=False, method="multi", chunksize=1000)
print(f"✅ Loaded {len(df):,} rows into public.nhs_daily")
