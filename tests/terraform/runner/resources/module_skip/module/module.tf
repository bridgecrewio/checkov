#
# WARNING: Line numbers matter in this test!
#          Update test_module_skip if a change is made!
#

# Bucket that will fail (no encryption) defined INSIDE a module
resource "aws_s3_bucket" "inside" {
  bucket = "inside-bucket"
}

resource "aws_s3_bucket" "inside2" {
  bucket = "inside-bucket-2"
}

module "another_module" {
  source = "../another/module"
}
