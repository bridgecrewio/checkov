variable "BUCKET_NAME" {
  type = string
  default = "this-is-my-default"
}

resource "aws_s3_bucket" "test" {
  bucket = var.BUCKET_NAME
}
