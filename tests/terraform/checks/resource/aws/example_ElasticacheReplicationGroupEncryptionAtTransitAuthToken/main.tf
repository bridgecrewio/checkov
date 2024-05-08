resource "aws_elasticache_replication_group" "pass" {
  automatic_failover_enabled    = true
  replication_group_id          = "tf-rep-group-1"
  node_type                     = "cache.m4.large"
  parameter_group_name          = "default.redis3.2"
  port                          = 6379
  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = true
  auth_token                    = var.auth_token
}

resource "aws_elasticache_replication_group" "pass2" {
  replication_group_id = local.replication_group_id
  description = "Sample Redis replication group"
  engine = "redis"
  transit_encryption_enabled = true
  user_group_ids = [
    "sample-group-id"
  ]
}

resource "aws_elasticache_replication_group" "fail" {
  automatic_failover_enabled    = true
  replication_group_id          = "tf-rep-group-2"
  node_type                     = "cache.m4.large"
  parameter_group_name          = "default.redis3.2"
  port                          = 6379
  at_rest_encryption_enabled    = false
  transit_encryption_enabled    = false
}

resource "aws_elasticache_replication_group" "fail2" {
  automatic_failover_enabled    = true
  replication_group_id          = "tf-rep-group-2"
  node_type                     = "cache.m4.large"
  parameter_group_name          = "default.redis3.2"
  port                          = 6379
  at_rest_encryption_enabled    = false
  transit_encryption_enabled    = false
  user_group_ids = [
    "sample-group-id"
  ]
}

resource "aws_elasticache_replication_group" "fail3" {
  automatic_failover_enabled    = true
  replication_group_id          = "tf-rep-group-2"
  node_type                     = "cache.m4.large"
  parameter_group_name          = "default.redis3.2"
  port                          = 6379
  at_rest_encryption_enabled    = false
  transit_encryption_enabled    = true
}
