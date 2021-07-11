provider "aws" {
  profile    = var.aws_profile
  region     = "us-east-1"
  alias  = "east1"
}

locals {
  dummy_with_dash      = format("-%s", var.dummy_1)
  bucket_name          = var.bucket_name
  x = {
    y = "z"
  }
}
resource "aws_instance" "example" {
  ami           = local.ami_name
  instance_type = module.child.myoutput
}

resource "aws_s3_bucket" "template_bucket" {
  provider      = aws.east1
  region        = var.region
  bucket        = local.bucket_name
  acl           = var.acl
  force_destroy = true
}

resource "aws_eip" "ip" {
    vpc = local.is_vpc
    instance = aws_instance.example.id
}

locals {
	is_vpc = true
	ami_name = local.dummy_with_dash
}

module "child" {
  source = "./child"
}