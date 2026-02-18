resource "awscc_redshift_cluster" "pass" {
  cluster_identifier = "redshift-encrypted"
  node_type          = "dc2.large"
  master_username    = "admin"
  master_user_password = "Password123"
  encrypted          = true
}

resource "awscc_redshift_cluster" "fail" {
  cluster_identifier = "redshift-unencrypted"
  node_type          = "dc2.large"
  master_username    = "admin"
  master_user_password = "Password123"
  encrypted          = false
}

resource "awscc_redshift_cluster" "fail2" {
  cluster_identifier = "redshift-default"
  node_type          = "dc2.large"
  master_username    = "admin"
  master_user_password = "Password123"
  # encrypted defaults to false
}
