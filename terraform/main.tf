terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- S3 data lake (private, versioned, encrypted) ---
resource "aws_s3_bucket" "data_lake" {
  bucket        = var.bucket_name
  force_destroy = false
  tags = {
    project = "nhs-etl"
    env     = var.env
  }
}

resource "aws_s3_bucket_versioning" "v" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "sse" {
  bucket = aws_s3_bucket.data_lake.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "pab" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Deny non-TLS access (defense-in-depth)
data "aws_iam_policy_document" "tls_only" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.data_lake.arn,
      "${aws_s3_bucket.data_lake.arn}/*"
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "tls_policy" {
  bucket = aws_s3_bucket.data_lake.id
  policy = data.aws_iam_policy_document.tls_only.json
}

# --- Least-privilege policy for ETL (read/write bronze & silver) ---
data "aws_iam_policy_document" "etl_access" {
  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data_lake.arn]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["bronze/*", "silver/*"]
    }
  }

  statement {
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:PutObject"]
    resources = [
      "${aws_s3_bucket.data_lake.arn}/bronze/*",
      "${aws_s3_bucket.data_lake.arn}/silver/*"
    ]
  }
}

resource "aws_iam_policy" "etl_policy" {
  name   = "${var.bucket_name}-etl-s3"
  policy = data.aws_iam_policy_document.etl_access.json
}

# Optional: attach the policy to an existing IAM user or role
resource "aws_iam_user_policy_attachment" "attach_user" {
  count      = var.attach_to_user_name != "" ? 1 : 0
  user       = var.attach_to_user_name
  policy_arn = aws_iam_policy.etl_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_role" {
  count      = var.attach_to_role_name != "" ? 1 : 0
  role       = var.attach_to_role_name
  policy_arn = aws_iam_policy.etl_policy.arn
}