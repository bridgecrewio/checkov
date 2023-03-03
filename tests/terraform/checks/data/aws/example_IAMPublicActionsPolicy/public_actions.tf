resource "aws_sns_topic" "some-topic" {}

data "aws_iam_policy_document" "fail" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    resources = [aws_sns_topic.some-topic.arn]
  }
}


data "aws_iam_policy_document" "pass" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["some:arn"]
    }
    resources = [aws_sns_topic.some-topic.arn]
  }
}


data "aws_iam_policy_document" "pass3" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = 3
    }
    resources = [aws_sns_topic.some-topic.arn]
  }
}


data "aws_iam_policy_document" "pass1" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = []
    }
    resources = [aws_sns_topic.some-topic.arn]
  }
}

data "aws_iam_policy_document" "pass2" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    condition {
      test     = "ArnLike"
      values   = ["arn:aws:service:region:accountId:resourceType/resourceId"]
      variable = "aws:PrincipalArn"
    }
    resources = [aws_sns_topic.some-topic.arn]
  }
}


data "aws_iam_policy_document" "fail2" {
  statement {

    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    condition {
      test     = "ArnLike"
      values   = ["arn:aws:service:region:accountId:resourceType/resourceId"]
      variable = "aws:PrincipalArn"
    }
    resources = [aws_sns_topic.some-topic.arn]
  }

  statement {
    actions = ["sns:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [aws_sns_topic.some-topic.arn]
  }
}


data "aws_iam_policy_document" "pass4" {
   statement {
     sid = "DenyObjectDelete"

     principals {
       type        = "AWS"
       identifiers = ["*"]
     }

     effect = "Deny"
     actions = ["s3:DeleteObject"]
     resources = ["${aws_s3_bucket.migrations.arn}/*"]
   }
}