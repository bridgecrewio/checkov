resource "aws_s3_bucket" "default" {
  count         = module.this.enabled ? 1 : 0
  bucket        = module.this.id
  acl           = try(length(var.grants), 0) == 0 ? var.acl : null
  force_destroy = var.force_destroy
  policy        = var.policy
  tags          = module.this.tags

  versioning {
    enabled = var.versioning_enabled
  }

  lifecycle_rule {
    id                                     = module.this.id
    enabled                                = var.lifecycle_rule_enabled
    prefix                                 = var.prefix
    tags                                   = var.lifecycle_tags
    abort_incomplete_multipart_upload_days = var.abort_incomplete_multipart_upload_days

    noncurrent_version_expiration {
      days = var.noncurrent_version_expiration_days
    }

    dynamic "noncurrent_version_transition" {
      for_each = var.enable_glacier_transition ? [1] : []

      content {
        days          = var.noncurrent_version_transition_days
        storage_class = "GLACIER"
      }
    }

    dynamic "transition" {
      for_each = var.enable_glacier_transition ? [1] : []

      content {
        days          = var.glacier_transition_days
        storage_class = "GLACIER"
      }
    }

    dynamic "transition" {
      for_each = var.enable_standard_ia_transition ? [1] : []

      content {
        days          = var.standard_transition_days
        storage_class = "STANDARD_IA"
      }
    }

    expiration {
      days = var.expiration_days
    }
  }

  dynamic "logging" {
    for_each = var.logging == null ? [] : [1]
    content {
      target_bucket = var.logging["bucket_name"]
      target_prefix = var.logging["prefix"]
    }
  }

  # https://docs.aws.amazon.com/AmazonS3/latest/dev/bucket-encryption.html
  # https://www.terraform.io/docs/providers/aws/r/s3_bucket.html#enable-default-server-side-encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = var.sse_algorithm
        kms_master_key_id = var.kms_master_key_arn
      }
    }
  }

  dynamic "cors_rule" {
    for_each = var.cors_rule_inputs == null ? [] : var.cors_rule_inputs

    content {
      allowed_headers = cors_rule.value.allowed_headers
      allowed_methods = cors_rule.value.allowed_methods
      allowed_origins = cors_rule.value.allowed_origins
      expose_headers  = cors_rule.value.expose_headers
      max_age_seconds = cors_rule.value.max_age_seconds
    }
  }

  dynamic "grant" {
    for_each = try(length(var.grants), 0) == 0 || try(length(var.acl), 0) > 0 ? [] : var.grants

    content {
      id          = grant.value.id
      type        = grant.value.type
      permissions = grant.value.permissions
      uri         = grant.value.uri
    }
  }

  dynamic "replication_configuration" {
    for_each = var.s3_replication_enabled ? [1] : []

    content {
      role = aws_iam_role.replication[0].arn

      dynamic "rules" {
        for_each = var.replication_rules == null ? [] : var.replication_rules

        content {
          id       = rules.value.id
          priority = try(rules.value.priority, 0)
          prefix   = try(rules.value.prefix, null)
          status   = try(rules.value.status, null)

          destination {
            bucket             = var.s3_replica_bucket_arn
            storage_class      = try(rules.value.destination.storage_class, "STANDARD")
            replica_kms_key_id = try(rules.value.destination.replica_kms_key_id, null)
            account_id         = try(rules.value.destination.account_id, null)

            dynamic "access_control_translation" {
              for_each = try(rules.value.destination.access_control_translation.owner, null) == null ? [] : [rules.value.destination.access_control_translation.owner]

              content {
                owner = access_control_translation.value
              }
            }
          }

          dynamic "source_selection_criteria" {
            for_each = try(rules.value.source_selection_criteria.sse_kms_encrypted_objects.enabled, null) == null ? [] : [rules.value.source_selection_criteria.sse_kms_encrypted_objects.enabled]

            content {
              sse_kms_encrypted_objects {
                enabled = source_selection_criteria.value
              }
            }
          }

          dynamic "filter" {
            for_each = try(rules.value.filter, null) == null ? [] : [rules.value.filter]

            content {
              prefix = try(filter.value.prefix, null)
              tags   = try(filter.value.tags, {})
            }
          }
        }
      }
    }
  }
}

module "s3_user" {
  source       = "git::https://github.com/cloudposse/terraform-aws-iam-s3-user.git?ref=tags/0.11.0"
  enabled      = module.this.enabled && var.user_enabled ? true : false
  s3_actions   = var.allowed_bucket_actions
  s3_resources = ["${join("", aws_s3_bucket.default.*.arn)}/*", join("", aws_s3_bucket.default.*.arn)]

  context = module.this.context
}

data "aws_partition" "current" {}

data "aws_iam_policy_document" "bucket_policy" {
  count = module.this.enabled && var.allow_encrypted_uploads_only ? 1 : 0

  statement {
    sid       = "DenyIncorrectEncryptionHeader"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["arn:${data.aws_partition.current.partition}:s3:::${join("", aws_s3_bucket.default.*.id)}/*"]

    principals {
      identifiers = ["*"]
      type        = "*"
    }

    condition {
      test     = "StringNotEquals"
      values   = [var.sse_algorithm]
      variable = "s3:x-amz-server-side-encryption"
    }
  }

  statement {
    sid       = "DenyUnEncryptedObjectUploads"
    effect    = "Deny"
    actions   = ["s3:PutObject"]
    resources = ["arn:${data.aws_partition.current.partition}:s3:::${join("", aws_s3_bucket.default.*.id)}/*"]

    principals {
      identifiers = ["*"]
      type        = "*"
    }

    condition {
      test     = "Null"
      values   = ["true"]
      variable = "s3:x-amz-server-side-encryption"
    }
  }
}

resource "aws_s3_bucket_policy" "default" {
  count      = module.this.enabled && var.allow_encrypted_uploads_only ? 1 : 0
  bucket     = join("", aws_s3_bucket.default.*.id)
  policy     = join("", data.aws_iam_policy_document.bucket_policy.*.json)
  depends_on = [aws_s3_bucket_public_access_block.default]
}

# Refer to the terraform documentation on s3_bucket_public_access_block at
# https://www.terraform.io/docs/providers/aws/r/s3_bucket_public_access_block.html
# for the nuances of the blocking options
resource "aws_s3_bucket_public_access_block" "default" {
  count  = module.this.enabled ? 1 : 0
  bucket = join("", aws_s3_bucket.default.*.id)

  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}

