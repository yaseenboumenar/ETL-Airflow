output "read_bucket"  { value = aws_s3_bucket.read.bucket }
output "write_bucket" { value = aws_s3_bucket.write.bucket }
output "region"       { value = var.region }
output "airflow_env"  { value = local_file.airflow_env.filename }