# scripts/transform_pandas.py
import os, io
import boto3
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

# <-- read the two env vars the DAG passes
READ_BUCKET  = os.getenv("READ_BUCKET_NAME",  "nhs-etl-datasets")
WRITE_BUCKET = os.getenv("WRITE_BUCKET_NAME", "nhs-etl-ingest-dev")

RAW_KEY    = "raw/nhs_data.csv"
SILVER_KEY = "silver/nhs_data/nhs_data.parquet"

print(f"Using READ_BUCKET={READ_BUCKET}, WRITE_BUCKET={WRITE_BUCKET}")
s3 = boto3.client("s3")

# Read raw CSV from READ bucket
obj = s3.get_object(Bucket=READ_BUCKET, Key=RAW_KEY)
df  = pd.read_csv(io.BytesIO(obj["Body"].read()))

# --- your light transform ---
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
if "report_date" in df.columns:
    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
df = df.drop_duplicates()

# Write Parquet to WRITE bucket
table = pa.Table.from_pandas(df)
buf = io.BytesIO()
pq.write_table(table, buf)
s3.put_object(Bucket=WRITE_BUCKET, Key=SILVER_KEY, Body=buf.getvalue())

print(f"✅ Wrote cleaned parquet to s3://{WRITE_BUCKET}/{SILVER_KEY}")