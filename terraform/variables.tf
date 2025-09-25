variable "region"          { type = string, default = "eu-north-1" }
variable "profile"         { type = string, default = null }
variable "project_prefix"  { type = string, default = "nhs-etl" }

variable "read_bucket_name"  { type = string, default = "nhs-etl-ingestion" }
variable "write_bucket_name" { type = string, default = "nhs-etl-dataset-silver" }

# Optional: seed your demo CSV
variable "seed_csv_path" {
  type        = string
  default     = "../datasets/nhs_data.csv"
  description = "Local path to CSV to upload to raw/ in ingestion bucket"
}