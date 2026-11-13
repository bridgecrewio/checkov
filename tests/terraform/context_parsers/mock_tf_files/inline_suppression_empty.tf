resource "aws_s3_bucket" "empty-skip-comment" {
  region        = "var.region"
    #checkov:skip=
  bucket        = "local.bucket_name"
  force_destroy = true
  acl           = "public-read"
}
