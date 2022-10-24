resource "aws_memorydb_cluster" "fail" {
  acl_name                 = "open-access"
  name                     = "my-cluster"
  node_type                = "db.t4g.small"
  num_shards               = 2
  security_group_ids       = [aws_security_group.example.id]
  snapshot_retention_limit = 7
  subnet_group_name        = aws_memorydb_subnet_group.example.id
}


resource "aws_memorydb_cluster" "pass" {
  acl_name                 = "open-access"
  name                     = "my-cluster"
  node_type                = "db.t4g.small"
  num_shards               = 2
  security_group_ids       = [aws_security_group.example.id]
  snapshot_retention_limit = 7
  subnet_group_name        = aws_memorydb_subnet_group.example.id
  kms_key_arn              = aws_kms_key.example.arn
}

resource "aws_kms_key" "example" {}