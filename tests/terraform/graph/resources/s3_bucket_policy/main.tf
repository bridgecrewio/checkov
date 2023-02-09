resource "aws_s3_bucket" "good" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket_policy" "good" {
  bucket = aws_s3_bucket.good.id
  policy = data.aws_iam_policy_document.good.json
}

data "aws_iam_policy_document" "good" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:Describe*",
    ]
    resources = [
      "arn:aws:s3:::examplebucket",
    ]
  }
}

resource "aws_s3_bucket" "bad" {
  bucket = "bucket_good"
}

resource "aws_s3_bucket_policy" "bad" {
  bucket = aws_s3_bucket.bad.id
  policy = data.aws_iam_policy_document.bad.json
}

data "aws_iam_policy_document" "bad" {
  version = "2012-10-17"

  statement {
    effect = "Allow"
    actions = [
      "s3:Describe*",
    ]
    resources = [
      "*",
    ]
  }
}
