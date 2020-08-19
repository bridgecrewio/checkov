resource "aws_s3_bucket" "b1" {
  bucket = "test-bucket"
  versioning {
    enabled = true
  }
}

resource "aws_security_group" "sg" {
  name = "test-sg"

  tags = {}
}

resource "aws_security_group" "sg2" {
  name = "test-sg"

  tags = {
    Owner = "owner"
  }
}

resource "aws_security_group" "sg3" {
  name = "test-sg"

  tags = {
    Owner = "owner"
    Hi = "hello"
  }
}

resource "aws_athena_database" "no-tags-needed" {
  name = "test"
  bucket = "bucket"
}
