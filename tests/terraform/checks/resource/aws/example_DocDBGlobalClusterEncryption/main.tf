resource "aws_docdb_global_cluster" "fail" {
  global_cluster_identifier = "global-test"
  engine                    = "docdb"
  engine_version            = "4.0.0"
}

resource "aws_docdb_global_cluster" "fail2" {
  global_cluster_identifier = "global-test"
  engine                    = "docdb"
  engine_version            = "4.0.0"
  storage_encrypted = false
}

resource "aws_docdb_global_cluster" "pass" {
  global_cluster_identifier = "global-test"
  engine                    = "docdb"
  engine_version            = "4.0.0"
  storage_encrypted = true
}