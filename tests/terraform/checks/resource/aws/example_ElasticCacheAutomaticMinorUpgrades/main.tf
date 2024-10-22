# pass

resource "aws_elasticache_cluster" "pass" {
  cluster_id           = "cluster"
  engine               = "redis"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  auto_minor_version_upgrade = true
  snapshot_retention_limit = 5
}

resource "aws_elasticache_cluster" "pass2" {
  cluster_id           = "cluster"
  engine               = "redis"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
}

resource "aws_elasticache_cluster" "fail" {
  cluster_id           = "cluster"
  engine               = "redis"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  auto_minor_version_upgrade = false
  snapshot_retention_limit = 0
}

# unknown

resource "aws_elasticache_cluster" "memcached" {
  cluster_id           = "cluster"
  engine               = "memcached"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.memcached1.6 "
}
