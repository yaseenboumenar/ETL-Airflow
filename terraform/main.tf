locals {
  tags = {
    Project = var.project_prefix
    Env     = "dev"
  }
}

# ---------- Ingestion (read) bucket ----------
resource "aws_s3_bucket" "read" {
  bucket        = var.read_bucket_name
  force_destroy = true        # dev convenience; remove in prod
  tags          = local.tags
}

resource "aws_s3_bucket_ownership_controls" "read" {
  bucket = aws_s3_bucket.read.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "read" {
  bucket                  = aws_s3_bucket.read.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "read" {
  bucket = aws_s3_bucket.read.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "read" {
  bucket = aws_s3_bucket.read.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# ---------- Silver (write) bucket ----------
resource "aws_s3_bucket" "write" {
  bucket        = var.write_bucket_name
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_ownership_controls" "write" {
  bucket = aws_s3_bucket.write.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_public_access_block" "write" {
  bucket                  = aws_s3_bucket.write.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "write" {
  bucket = aws_s3_bucket.write.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "write" {
  bucket = aws_s3_bucket.write.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Optional: deny non-SSL
data "aws_iam_policy_document" "ssl_only" {
  statement {
    sid     = "DenyInsecureTransport"
    effect  = "Deny"
    actions = ["s3:*"]
    principals {
        type = "*"
        identifiers = ["*"] 
      }
    resources = [
      aws_s3_bucket.read.arn,  "${aws_s3_bucket.read.arn}/*",
      aws_s3_bucket.write.arn, "${aws_s3_bucket.write.arn}/*",
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "ssl_read" {
  bucket = aws_s3_bucket.read.id
  policy = data.aws_iam_policy_document.ssl_only.json
}

resource "aws_s3_bucket_policy" "ssl_write" {
  bucket = aws_s3_bucket.write.id
  policy = data.aws_iam_policy_document.ssl_only.json
}

# Optional: seed demo CSV to ingestion bucket at raw/nhs_data.csv
resource "aws_s3_object" "seed_csv" {
  bucket = aws_s3_bucket.read.id
  key    = "raw/nhs_data.csv"
  source = var.seed_csv_path
  etag   = filemd5(var.seed_csv_path)
}

# Generate an env file used by Docker Compose
resource "local_file" "airflow_env" {
  filename = "${path.module}/../.env.airflow"
  content  = <<EOF
READ_BUCKET_NAME=${aws_s3_bucket.read.bucket}
WRITE_BUCKET_NAME=${aws_s3_bucket.write.bucket}
AWS_DEFAULT_REGION=${var.region}
EOF
}