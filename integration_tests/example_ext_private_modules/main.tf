module "s3_bucket" {
  source = "github.com/ckv-tests/terraform-aws-s3-bucket-private"
  version = "0.0.1"
  acl                      = "public"
  enabled                  = true
}

module "s3-bucket1" {
  source  = "app.terraform.io/panw-bridgecrew/s3-bucket1/aws"
  version = "0.0.2"
}