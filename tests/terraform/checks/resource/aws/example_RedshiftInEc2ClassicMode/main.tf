resource "aws_redshift_cluster" "fail" {
  cluster_identifier = "redshift-defaults-only"
  node_type = "dc2.large"
  master_password = "Test1234"
  master_username = "test"
  skip_final_snapshot = true
}

resource "aws_redshift_cluster" "pass" {
  cluster_identifier = "redshift-defaults-only"
  node_type = "dc2.large"
  master_password = "Test1234"
  master_username = "test"
  skip_final_snapshot = true
  cluster_subnet_group_name="subnet-ebd9cead"
}
