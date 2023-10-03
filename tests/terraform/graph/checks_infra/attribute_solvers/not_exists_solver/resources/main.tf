provider "aws" {
  region = "us-east-1"
}
resource "aws_s3_bucket" "test" {
  bucket = "comp-s3-all-rql-nov10-22"
  tags   = { test = "demo" }
}
resource "aws_s3_bucket_policy" "allow_access" {
  bucket = aws_s3_bucket.test.id
  policy = <<POLICY
          {
      "Version": "2012-10-17",
      "Statement": [{
            "Sid": "statement-1",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "${aws_s3_bucket.test.arn}",
            "Condition":{"Bool":{"aws:SecureTransport": "false"}}
            },
            {
            "Sid": "statement-2",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "*",
            "Resource": "${aws_s3_bucket.test.arn}",
            "Condition":{"Bool":{"aws:SecureTransport": "false"}}
            }
            ]}
POLICY
}