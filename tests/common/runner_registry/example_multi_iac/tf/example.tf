variable "region" {
  default = "us-east-1"
}
variable "VERSIONING_ENABLED" {}

resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  force_destroy = true
  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  versioning {
    enabled = var.VERSIONING_ENABLED
    mfa_delete = true
  }
  logging {
    target_bucket = "${aws_s3_bucket.log_bucket.id}"
    target_prefix = "log/"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.mykey.arn}"
        sse_algorithm     = "aws:kms"
      }
    }
  }
  acl           = "private"
}
data "aws_caller_identity" "current" {}

resource aws_rds_cluster "rds_cluster" {}

resource aws_rds_cluster_instance "rds_cluster_public" {
  cluster_identifier = "id"
  instance_class = "foo-bar"
  publicly_accessible = false
}
