locals {
  dummy_with_dash  = format("-%s", var.dummy_1)
  dummy_with_comma = format(":%s", var.dummy_1)
  bucket_name      = var.bucket_name
}

variable "user_exists" {
  default = false
}

resource "aws_cognito_user_group" "user_group" {
  name         = "${var.customer_name}_group"
  description  = "${var.customer_name} user group"
  user_pool_id = var.user_pool_id
}

resource "null_resource" "create_cognito_user" {
  count = var.user_exists ? 0 : 1
  triggers = {
    build_number = var.user_email
  }

  provisioner "local-exec" {
    command = "aws --profile=${var.aws_profile} --region=${var.region} cognito-idp admin-create-user --user-pool-id ${var.user_pool_id} --username ${var.user_email}"
  }
}

resource "aws_iam_account_password_policy" "password-policy" {
  minimum_password_length        = 15
  require_lowercase_characters   = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_symbols                = true
  allow_users_to_change_password = true
}

data "aws_iam_policy_document" "event_stream_bucket_role_assume_role_policy" {
  statement {
    actions = [var.action]

    resources = [
      "*",
      "abc"
    ]
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }

    principals {
      type        = "AWS"
      identifiers = var.trusted_role_arn
    }
  }
}

resource "aws_s3_bucket" "template_bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = var.acl
  force_destroy = true
}