output "bucket" {
  value = aws_s3_bucket.data_lake.bucket
}

output "etl_policy_arn" {
  value = aws_iam_policy.etl_policy.arn
}