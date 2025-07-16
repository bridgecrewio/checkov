#
# WARNING: Line numbers matter in this test!
#          Update test_module_failure_reporting_772 if a change is made!
#

module "test_module" {
  source = "./module"
}

# Bucket that will fail (no encryption) defined OUTSIDE a module
resource "aws_s3_bucket" "outside" {
  bucket = "outside-bucket"

  object_lock_configuration {
    object_lock_enabled = "Disabled"
  }
}