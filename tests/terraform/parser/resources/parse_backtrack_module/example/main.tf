module "bucket_local" {
  source = "../"

  bucket_name = var.name
}

# the remote module needs to be at the end to properly test the issue
module "bucket_remote" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "remote"
}
