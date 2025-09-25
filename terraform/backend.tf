terraform {
  backend "s3" {
    bucket = "nhs-etl-tfstate"
    key    = "infra/terraform.tfstate"
    region = "eu-north-1"
    encrypt = true
  }
}