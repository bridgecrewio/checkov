resource "aws_neptune_cluster_snapshot" "fail" {
  db_cluster_identifier          = aws_neptune_cluster.example.id
  db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
}

resource "aws_neptune_cluster_snapshot" "fail2" {
  db_cluster_identifier          = aws_neptune_cluster.example.id
  db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
  storage_encrypted = false
}

resource "aws_neptune_cluster_snapshot" "pass" {
  db_cluster_identifier          = aws_neptune_cluster.example.id
  db_cluster_snapshot_identifier = "resourcetestsnapshot1234"
  storage_encrypted =true
}