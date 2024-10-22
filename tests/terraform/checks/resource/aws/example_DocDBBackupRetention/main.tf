# pass

resource "aws_docdb_cluster" "pass" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret

  backup_retention_period = 7
}



# fail

resource "aws_docdb_cluster" "fail_no_value" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret
}


resource "aws_docdb_cluster" "fail_value_not_adequate" {
  cluster_identifier = "my-docdb-cluster"
  engine             = "docdb"
  master_username    = "foo"
  master_password    = "mustbeeightchars"  # checkov:skip=CKV_SECRET_6 test secret

  backup_retention_period = 3
}