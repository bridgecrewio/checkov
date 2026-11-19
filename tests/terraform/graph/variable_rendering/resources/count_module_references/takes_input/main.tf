variable "bucket_id" {}

resource "aws_s3_bucket_versioning" "takes_input" {
  bucket = var.bucket_id
}
