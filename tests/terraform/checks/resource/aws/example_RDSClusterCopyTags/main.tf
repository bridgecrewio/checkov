resource "aws_rds_cluster" "fail" {
  cluster_identifier        = "example"
  availability_zones        = ["us-west-2a", "us-west-2b", "us-west-2c"]
  engine                    = "mysql"
  db_cluster_instance_class = "db.r6gd.xlarge"
  storage_type              = "io1"
  allocated_storage         = 100
  iops                      = 1000
  master_username           = "test"
  master_password           = "mustbeeightcharaters"  # checkov:skip=CKV_SECRET_6 test secret
}

resource "aws_rds_cluster" "fail2" {
  cluster_identifier        = "example"
  availability_zones        = ["us-west-2a", "us-west-2b", "us-west-2c"]
  engine                    = "mysql"
  db_cluster_instance_class = "db.r6gd.xlarge"
  storage_type              = "io1"
  allocated_storage         = 100
  iops                      = 1000
  master_username           = "test"
  master_password           = "mustbeeightcharaters"
  copy_tags_to_snapshot = false
}

resource "aws_rds_cluster" "pass" {
  cluster_identifier        = "example"
  availability_zones        = ["us-west-2a", "us-west-2b", "us-west-2c"]
  engine                    = "mysql"
  db_cluster_instance_class = "db.r6gd.xlarge"
  storage_type              = "io1"
  allocated_storage         = 100
  iops                      = 1000
  master_username           = "test"
  master_password           = "mustbeeightcharaters"
  copy_tags_to_snapshot = true
}