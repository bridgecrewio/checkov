resource "aws_docdb_cluster" "fail" {
  cluster_identifier  = "mycluster"
  availability_zones  = [data.aws_availability_zones.available.names[0], data.aws_availability_zones.available.names[1], data.aws_availability_zones.available.names[2]]
  master_username     = "foo"
  master_password     = "mustbeeightcharaters"  # checkov:skip=CKV_SECRET_6 test secret
  storage_encrypted   = true
  skip_final_snapshot = true
}

resource "aws_docdb_cluster" "pass" {
  cluster_identifier  = "mycluster"
  availability_zones  = [data.aws_availability_zones.available.names[0], data.aws_availability_zones.available.names[1], data.aws_availability_zones.available.names[2]]
  master_username     = "foo"
  master_password     = "mustbeeightcharaters"
  storage_encrypted   = true
  kms_key_id          = aws_kms_key.foo.arn
  skip_final_snapshot = true
}