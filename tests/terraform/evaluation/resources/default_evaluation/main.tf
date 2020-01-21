locals {
  dummy_with_dash      = format("-%s", var.dummy_1)
  dummy_with_comma     = format(":%s", var.dummy_1)
  bucket_name          = var.bucket_name
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

resource "aws_s3_bucket" "template_bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = var.acl
  force_destroy = true
}