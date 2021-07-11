resource "aws_rds_cluster" "rds_cluster_encrypted" {
  cluster_identifier = "some-encrypted-id"
  kms_key_id = "some-kms-key-id"
}

resource "aws_rds_cluster" "rds_cluster_unencrypted" {
  cluster_identifier = "some-unencrypted-id"
}

resource "aws_s3_bucket" "encrypted_bucket" {
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket" "unencrypted_bucket" {
  versioning {
    enabled = True
  }
}

resource "aws_neptune_cluster" "encrypted_neptune" {
  cluster_identifier = "encrypted-neptune"
  storage_encrypted = true
}

resource "aws_neptune_cluster" "unencrypted_neptune" {
  cluster_identifier = "unencrypted-neptune"
}
