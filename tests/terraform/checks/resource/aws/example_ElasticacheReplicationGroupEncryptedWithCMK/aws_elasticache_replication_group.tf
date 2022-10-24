resource "aws_elasticache_replication_group" "pass" {
  replication_group_id          = "tf-%s"
  replication_group_description = "test description"
  node_type                     = "cache.t2.micro"
  number_cache_clusters         = "1"
  port                          = 6379
  subnet_group_name             = aws_elasticache_subnet_group.bar.name
  security_group_ids            = [aws_security_group.bar.id]
  parameter_group_name          = "default.redis3.2"
  availability_zones            = [data.aws_availability_zones.available.names[0]]
  engine_version                = "3.2.6"
  at_rest_encryption_enabled    = true
  kms_key_id                    = aws_kms_key.bar.arn
}

resource "aws_elasticache_replication_group" "fail" {
  replication_group_id          = "tf-%s"
  replication_group_description = "test description"
  node_type                     = "cache.t2.micro"
  number_cache_clusters         = "1"
  port                          = 6379
  subnet_group_name             = aws_elasticache_subnet_group.bar.name
  security_group_ids            = [aws_security_group.bar.id]
  parameter_group_name          = "default.redis3.2"
  availability_zones            = [data.aws_availability_zones.available.names[0]]
  engine_version                = "3.2.6"
  at_rest_encryption_enabled    = true
}