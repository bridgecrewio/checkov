# pass

resource "aws_elasticache_cluster" "pass" {
  cluster_id           = "cluster"
  engine               = "redis"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  subnet_group_name    = "mysubnet"
  snapshot_retention_limit = 5
}

resource "aws_elasticache_cluster" "fail" {
  cluster_id           = "cluster"
  engine               = "redis"
  node_type            = "cache.m5.large"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  snapshot_retention_limit = 0
}
