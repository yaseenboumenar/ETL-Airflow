# scripts/load_postgres.py
import os, io, boto3, pyarrow.parquet as pq
import pandas as pd
from sqlalchemy import create_engine

BUCKET = os.getenv("WRITE_BUCKET_NAME", "nhs-etl-ingestion")
PREFIX = os.getenv("SILVER_KEY", "silver/nhs_data/")  # allows overriding if needed

DB_URL = os.getenv(
    "DB_URL",
    "postgresql+psycopg2://etluser:etlpass@localhost:5432/etlwarehouse"  # for local runs
)

s3 = boto3.client("s3")

# list parquet parts under the folder
resp = s3.list_objects_v2(Bucket=BUCKET, Prefix=PREFIX)
keys = [c["Key"] for c in resp.get("Contents", []) if c["Key"].endswith(".parquet")]
if not keys:
    raise RuntimeError(f"No parquet parts found in s3://{BUCKET}/{PREFIX}")
part_key = sorted(keys)[0]  # pick the first part (demo scale)

obj = s3.get_object(Bucket=BUCKET, Key=part_key)
table = pq.read_table(io.BytesIO(obj["Body"].read()))
df = table.to_pandas()
print(f"✅ Read {len(df)} rows from s3://{BUCKET}/{part_key}")

engine = create_engine(DB_URL, future=True)
with engine.begin() as conn:
    print("✅ Connected to Postgres")

df.to_sql("nhs_daily", con=engine, schema="public",
          if_exists="replace", index=False, method="multi", chunksize=1000)
print(f"✅ Loaded {len(df):,} rows into public.nhs_daily")