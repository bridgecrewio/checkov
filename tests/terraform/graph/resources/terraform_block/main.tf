terraform {
  backend "s3" {
    encrypt = true
  }
  required_version = "1.1.5"
  required_providers {
    aws = {
      version = ">= 2.7.0"
      source = "hashicorp/aws"
    }
  }
}
