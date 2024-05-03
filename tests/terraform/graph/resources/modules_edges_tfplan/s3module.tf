module "s3-bucket-1" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.0.1"
}

module "s3-bucket-2" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.0.1"
}