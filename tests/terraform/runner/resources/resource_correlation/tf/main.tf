locals {
  region = "us-east-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "mybucket.${local.region}.mycompany.com"
  region = local.region

  tags = {
    data_classification = "public"
  }
}

resource "aws_s3_bucket_policy" "my_bucket_policy" {
  bucket = aws_s3_bucket.my_bucket.id
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Id": "my_bucket_policy",
    "Statement": [
        {
            "Sid": "IPAllow",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": [
                "arn:aws:s3:::${aws_s3_bucket.my_bucket.bucket}/*",
                "arn:aws:s3:::${aws_s3_bucket.my_bucket.bucket}"
            ],
            "Condition": {
                "StringLike": {
                    "aws:sourceVpce": ["vpc1", "vpc2", "vpc3"]
                }
            }
        }
    ]
}
POLICY
}
