import io, os, boto3, pandas as pd
import pyarrow as pa, pyarrow.parquet as pq

READ_BUCKET  = os.getenv("READ_BUCKET_NAME",  "nhs-etl-datasets")
WRITE_BUCKET = os.getenv("WRITE_BUCKET_NAME", "nhs-etl-datasets")
RAW_KEY = "raw/nhs_data.csv"
SILVER_KEY = "silver/nhs_data/nhs_data.parquet"

s3 = boto3.client("s3")

# Read raw .csv from s3
obj = s3.get_object(Bucket=BUCKET, Key=RAW_KEY)
df = pd.read_csv(io.BytesIO(obj["Body"].read()))

# --- light "real" ETL you'll keep expanding ---
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
if "report_date" in df.columns:
    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce")
df = df.drop_duplicates()

# Write back to s3 as Parquet (silver)
table = pa.Table.from_pandas(df)
buf = io.BytesIO()
pq.write_table(table, buf)
s3.put_object(Bucket=BUCKET, Key=SILVER_KEY, Body=buf.getvalue())

print("✅ Wrote cleaned parquet to s3://%s/%s" % (BUCKET, SILVER_KEY))