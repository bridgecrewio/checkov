# Bucket that will fail (no encryption) defined INSIDE a module
resource "aws_s3_bucket" "module" {
  bucket = "inside-bucket"

  object_lock_configuration {
    object_lock_enabled = "Disabled"
  }
}
