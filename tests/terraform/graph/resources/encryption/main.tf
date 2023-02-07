# Resource names in this file are **important**
# Encrypted resources _must_ start their name with the word "encrypted"
resource aws_ecr_repository "encrypted_repo" {
  name = "nimtest-repo"
  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource aws_ecr_repository "unencrypted_repo" {
  name = "nimtest-repo-unencrypted"
}

resource "aws_neptune_cluster" "encrypted_neptune" {
  storage_encrypted = true
  skip_final_snapshot = true
}

resource "aws_neptune_cluster" "unencrypted_neptune" {
  storage_encrypted = false
  skip_final_snapshot = true
}

resource "aws_efs_file_system" "encrypted_file_system" {
  encrypted = true
}

resource "aws_efs_file_system" "unencrypted_file_system" {
}

resource "aws_ebs_volume" "encrypted_volume" {
  availability_zone = "us-east-1a"
  encrypted = true
  size = 8
}

resource "aws_ebs_volume" "unencrypted_volume" {
  availability_zone = "us-east-1a"
  size = 8
}

resource "aws_ebs_volume" "unencrypted_volume2" {
  availability_zone = "us-east-1a"
  encrypted = false
  size = 8
}

resource "aws_elasticache_replication_group" "encrypted_replication_group" {
  replication_group_description = "nimtest replication group"
  replication_group_id = "nimtest"
  at_rest_encryption_enabled = true
  cluster_mode {
    num_node_groups = 0
    replicas_per_node_group = 0
  }
}

resource "aws_elasticache_replication_group" "unencrypted_replication_group" {
  replication_group_description = "nimtest replication group"
  replication_group_id = "nimtest"
  cluster_mode {
    num_node_groups = 0
    replicas_per_node_group = 0
  }
}

resource "aws_elasticsearch_domain" "encrypted_domain" {
  domain_name = "nimtest-encryption-test"
  encrypt_at_rest {
    enabled = true
  }
  node_to_node_encryption {
    enabled = true
  }
}

resource "aws_elasticsearch_domain" "unencrypted_domain" {
  domain_name = "nimtest-encryption-test"
  node_to_node_encryption {
    enabled = false
  }
}

resource "aws_msk_cluster" "encrypted_msk" {
  cluster_name = ""
  kafka_version = ""
  number_of_broker_nodes = 0
  broker_node_group_info {
    client_subnets = []
    ebs_volume_size = 0
    instance_type = ""
    security_groups = []
  }

  encryption_info {
    encryption_in_transit {
      in_cluster = true
      client_broker = "TLS"
    }
    encryption_at_rest_kms_key_arn = "KMS"
  }
}

resource "aws_kinesis_stream" "encrypted_stream" {
  name = "nimtest"
  shard_count = 1
  encryption_type = "KMS"
  kms_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_kinesis_stream" "unencrypted_stream" {
  name = "nimtest"
  shard_count = 1
}

resource "aws_s3_bucket" "encrypted_bucket_by_default" {
  bucket = "encrypted"
}

resource "aws_s3_bucket" "encrypted_bucket" {
  bucket = "unencrypted"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket" "encrypted_bucket_2" {
  bucket = "unencrypted"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_object" "encrypted_object_by_itself" {
  bucket = aws_s3_bucket.encrypted_bucket.bucket
  key = "some-key.html"

  server_side_encryption = "AES256"
}

resource "aws_s3_bucket_object" "unencrypted_object_by_bucket" {
  bucket = aws_s3_bucket.encrypted_bucket.bucket
  key = "some-key.html"
}

resource "aws_sns_topic" "encrypted_topic" {
  name = "encrypted"
  kms_master_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_sns_topic" "unencrypted_topic" {
  name = "unencrypted"
}

resource "aws_sqs_queue" "encrypted_queue" {
  name = "encrypted"
  kms_master_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_sqs_queue" "unencrypted_queue" {
  name = "unencrypted"
}

resource "aws_cloudwatch_log_group" "encrypted_by_default_cloudwatch_log_group" {
  name = "group"
}

resource "aws_cloudwatch_log_group" "encrypted" {
  name = "group"
  kms_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_cloudtrail" "encrypted" {
  name = "encrypted"
  s3_bucket_name = aws_s3_bucket.encrypted_bucket.bucket
  kms_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_cloudtrail" "unencrypted" {
  name = "encrypted"
  s3_bucket_name = aws_s3_bucket.encrypted_bucket.bucket
}

resource "aws_dynamodb_table" "encrypted" {
  name = "encrypted"
  hash_key = ""
  attribute {
    name = ""
    type = ""
  }
  server_side_encryption {
    enabled = true
  }
}

resource "aws_dynamodb_table" "encrypted_by_default_dynamodb_table" {
  name = "encrypted_by_default"
  hash_key = ""
  attribute {
    name = ""
    type = ""
  }
}

resource "aws_iam_role" "role" {
  assume_role_policy = ""
}

resource "aws_docdb_cluster" "encrypted_docdb" {
  storage_encrypted = true
  kms_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_docdb_cluster" "unencrypted_docdb" {
  storage_encrypted = false
}

resource "aws_codebuild_project" "encrypted_project" {
  name = "encrypted"
  service_role = ""
  artifacts {
    type = ""
  }
  environment {
    compute_type = ""
    image = ""
    type = ""
  }
  source {
    type = ""
  }

  encryption_key = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_codebuild_project" "unencrypted_project" {
  name = "unencrypted"
  service_role = ""
  artifacts {
    type = ""
  }
  environment {
    compute_type = ""
    image = ""
    type = ""
  }
  source {
    type = ""
  }
}

resource "aws_codebuild_report_group" "encrypted_report_group" {
  export_config {
    type = "S3"
    s3_destination {
      bucket = "some-bucket"
      encryption_disabled = false
      encryption_key = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
      packaging = "NONE"
      path = "/some/path"
    }
  }
}

resource "aws_codebuild_report_group" "unencrypted_report_group" {
  export_config {
    type = "S3"
    s3_destination {
      bucket = "some-bucket"
      encryption_disabled = true
      packaging = "NONE"
      path = "/some/path"
    }
  }
}

resource "aws_athena_database" "encrypted_athena_database" {
  bucket = ""
  name = "encrypted"
  encryption_configuration {
    encryption_option = "SSE_S3"
  }
}

resource "aws_athena_database" "unencrypted_athena_database" {
  bucket = ""
  name = "unencrypted"
}

resource "aws_athena_workgroup" "encrypted_workgroup" {
  name = "encrypted"
  configuration {
    result_configuration {
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
      }
    }
  }
}

resource "aws_athena_workgroup" "unencrypted_workgroup" {
  name = "unencrypted"
}

resource "aws_eks_cluster" "encrypted_eks" {
  name = ""
  role_arn = ""
  vpc_config {
    subnet_ids = []
  }

  encryption_config {
    resources = []
    provider {
      key_arn = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
    }
  }
}

resource "aws_db_instance" "encrypted_instance" {
  instance_class = ""

  storage_encrypted = true
}

resource "aws_db_instance" "unencrypted_instance" {
  instance_class = ""

  storage_encrypted = false
}

resource "aws_rds_cluster" "encrypted_rds_cluster" {
  storage_encrypted = true
  kms_key_id = "arn:aws:kms:us-east-1:000000000000:key/some-key-uuid"
}

resource "aws_rds_cluster" "unencrypted_rds_cluster" {
}

resource "aws_rds_global_cluster" "encrypted_global_rds" {
  global_cluster_identifier = "some-id"
  storage_encrypted = true
}

resource "aws_rds_global_cluster" "unencrypted_global_rds" {
  global_cluster_identifier = "some-id"
  storage_encrypted = false
}

resource "aws_s3_bucket_inventory" "encrypted_s3_inventory" {
  bucket = ""
  included_object_versions = ""
  name = ""
  destination {
    bucket {
      bucket_arn = ""
      format = ""
      encryption {
        sse_s3 {}
      }
    }
  }
  schedule {
    frequency = ""
  }
}

resource "aws_dax_cluster" "encrypted_dax_cluster" {
  cluster_name = "dax"
  iam_role_arn = ""
  node_type = ""
  replication_factor = 0
  server_side_encryption {
    enabled = true
  }
}

resource "aws_dax_cluster" "unencrypted_dax_cluster" {
  cluster_name = "dax"
  iam_role_arn = ""
  node_type = ""
  replication_factor = 0
  server_side_encryption {
    enabled = false
  }
}

resource "aws_redshift_cluster" "encrypted_redshift_cluster" {
  cluster_identifier = "redshift"
  node_type = ""
  encrypted = true
}

resource "aws_redshift_cluster" "unencrypted_redshift_cluster" {
  cluster_identifier = "redshift"
  node_type = ""
}
