#
# WARNING: Line numbers matter in this test!
#          Update test_module_failure_reporting_772 if a change is made!
#

# Bucket that will fail (no encryption) defined INSIDE a module
resource "aws_s3_bucket" "inside" {
  bucket = "inside-bucket"

  object_lock_configuration {
    object_lock_enabled = "Disabled"
  }
}