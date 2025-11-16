resource "aws_s3_bucket" "my_bucket" {
  for_each = toset(["logs", "assets"])
  bucket = "${each.key}-bucket"
}