# scripts/transform_spark.py
import os
from pyspark.sql import SparkSession, functions as F

READ_BUCKET  = os.getenv("READ_BUCKET_NAME",  "nhs-etl-ingestion")
WRITE_BUCKET = os.getenv("WRITE_BUCKET_NAME", "nhs-etl-dataset-silver")

RAW_KEY    = "raw/nhs_data.csv"
SILVER_DIR = "silver/nhs_data/"

spark = (
    SparkSession.builder
    .appName("nhs_transform_spark")
    # Bring S3 support jars (Hadoop + AWS SDK)
    .config("spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262")
    # Use default chain (env vars, ~/.aws/credentials, IAM if present)
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")
    .getOrCreate()
)

# 1) Read raw CSV from S3
src = f"s3a://{READ_BUCKET}/{RAW_KEY}"
df = (spark.read
      .option("header", True)
      .option("inferSchema", True)
      .csv(src))

# 2) Light clean
for c in df.columns:
    df = df.withColumnRenamed(c, c.strip().lower().replace(" ", "_"))

if "report_date" in df.columns:
    df = df.withColumn("report_date", F.to_date("report_date"))

df = df.dropDuplicates()

# 3) Write silver Parquet dataset to S3
dst = f"s3a://{WRITE_BUCKET}/{SILVER_DIR}"
(df.coalesce(1)  # single file for the demo; remove for real data
   .write.mode("overwrite")
   .parquet(dst))

print(f"✅ Spark wrote {df.count()} rows to {dst}")
spark.stop()