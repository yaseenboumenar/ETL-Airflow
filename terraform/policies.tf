# Force HTTPS only for the ingestion bucket
data "aws_iam_policy_document" "ssl_only_read" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    # IMPORTANT: only this bucket + its objects
    resources = [
      aws_s3_bucket.read.arn,
      "${aws_s3_bucket.read.arn}/*",
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
  policy = data.aws_iam_policy_document.ssl_only_read.json
}

# Force HTTPS only for the silver bucket
data "aws_iam_policy_document" "ssl_only_write" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.write.arn,
      "${aws_s3_bucket.write.arn}/*",
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "ssl_write" {
  bucket = aws_s3_bucket.write.id
  policy = data.aws_iam_policy_document.ssl_only_write.json
}