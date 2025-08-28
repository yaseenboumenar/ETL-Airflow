
variable "aws_region" {
  type = string
  default = "eu-north-1"
}

variable "env" {
  type = string
  default = "dev"
}

variable "bucket_name" {
  type = string
}

variable "attach_to_user_name" {
  type = string
  default = ""
}

variable "attach_to_role_name" {
  type = string
  default = ""
}