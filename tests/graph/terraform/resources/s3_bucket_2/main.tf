resource "aws_s3_bucket" "private" {
  bucket = "my-tf-test-bucket"
  acl    = "private"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket" "public" {
  bucket = "my-tf-test-bucket"
  acl    = "public"

  tags = {
    Name        = "My other bucket"
    Environment = "Prod"
  }
}

resource "aws_s3_bucket" "non_tag" {
  bucket = "no-tags"
  acl    = "public"
}
