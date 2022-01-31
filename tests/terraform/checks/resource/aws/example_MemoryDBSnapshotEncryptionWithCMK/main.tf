resource "aws_memorydb_snapshot" "pass" {
  cluster_name = aws_memorydb_cluster.example.name
  name_prefix  = aws_memorydb_cluster.example.name
  kms_key_arn  = aws_kms_key.example.arn
}

resource "aws_memorydb_cluster" "example" {
  acl_name                 = "open-access"
  name                     = "my-cluster"
  node_type                = "db.t4g.small"
  num_shards               = 2
  security_group_ids       = [aws_security_group.example.id]
  snapshot_retention_limit = 7
  subnet_group_name        = aws_memorydb_subnet_group.example.id
  kms_key_arn              = aws_kms_key.example.arn
}

resource "aws_memorydb_snapshot" "fail" {
  cluster_name = aws_memorydb_cluster.example.name
  name_prefix  = aws_memorydb_cluster.example.name
}


resource "aws_kms_key" "example" {}