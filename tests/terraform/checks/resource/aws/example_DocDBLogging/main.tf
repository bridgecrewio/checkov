# pass

resource "aws_docdb_cluster" "pass_single" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret

  enabled_cloudwatch_logs_exports = ["audit"]
}

resource "aws_docdb_cluster" "pass_double" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret

  enabled_cloudwatch_logs_exports = ["audit", "profiler"]
}

# fail

resource "aws_docdb_cluster" "fail" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret
}
