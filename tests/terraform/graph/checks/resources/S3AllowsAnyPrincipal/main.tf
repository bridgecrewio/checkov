
resource "aws_s3_bucket_policy" "fail" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.fail.json
}

data "aws_iam_policy_document" "fail" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.b.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "pass" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.pass.json
}

data "aws_iam_policy_document" "pass" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["some_arn"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.b.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "duff" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.duff.json
}

data "aws_iam_policy_document" "duff" {
#  statement {
#    principals {
#      type        = "AWS"
#      identifiers = ["some_arn"]
#    }
#    actions   = ["s3:GetObject"]
#    resources = ["${aws_s3_bucket.b.arn}/*"]
#  }
}

resource "aws_s3_bucket_policy" "fail2" {
  bucket = aws_s3_bucket.b.id
  policy = data.aws_iam_policy_document.fail2.json
}

data "aws_iam_policy_document" "fail2" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.b.arn}/*"]
  }
  statement {
    principals {
      type        = "AWS"
      identifiers = ["some_arn"]
    }
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.c.arn}/*"]
  }

}