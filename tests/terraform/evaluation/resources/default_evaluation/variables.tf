variable "customer_name" {
  default = "Pavel_Checkov"
}

variable "user_email" {
  default = "checkov@bridgecrew.io"
}

variable "bucket_name" {
  default = "MyBucket"
}

variable "acl" {
  default = "public-acl"
}

variable "action" {
  default = "*"
}

variable "trusted_role_arn" {
  default = "aws:arn:xxx:xxx"
}

variable "region" {
  default = "us-west-2"
}

variable "app_client_id" {
  description = "Indicates whether the app client has been created"
  default = "Temp"
}

variable "user_pool_id" {
  default = "123"
}

variable "aws_profile" {
  default = "default"
}

variable "dummy_1" {
  default = "dummy_1"
}

variable"user_exists"{
  default = false
}