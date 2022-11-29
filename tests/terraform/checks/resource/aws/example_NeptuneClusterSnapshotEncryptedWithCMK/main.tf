resource "aws_neptune_cluster_snapshot" "fail" {
  db_cluster_identifier          = aws_neptune_cluster.example.id
  db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
  storage_encrypted=true
}


resource "aws_neptune_cluster_snapshot" "pass" {
  db_cluster_identifier          = aws_neptune_cluster.example.id
  db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
  storage_encrypted = true
  kms_key_id = aws_kms_key.pike.id
}