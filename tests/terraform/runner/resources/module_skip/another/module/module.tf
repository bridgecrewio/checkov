# Bucket that will fail (no encryption) defined INSIDE a module
resource "aws_s3_bucket" "nested-inside" {
  bucket = "nested-inside-bucket"
}

# this module is used to test 3 layers deep
module "module-3" {
  source = "./module-3"
}
