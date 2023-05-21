
resource "aws_db_instance" "fail" {
  cluster_identifier      = "aurora-cluster-demo"
  availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
  database_name           = "mydb"
  master_username         = "foo"
  master_password         = "bar"
  backup_retention_period = 5
  preferred_backup_window = "07:00-09:00"
  deletion_protection     = false
  instance_class          = "m4.large"
}

resource "aws_db_instance" "fail2" {
  cluster_identifier           = "aurora-cluster-demo"
  availability_zones           = ["us-west-2a", "us-west-2b", "us-west-2c"]
  database_name                = "mydb"
  master_username              = "foo"
  master_password              = "bar"
  backup_retention_period      = 5
  preferred_backup_window      = "07:00-09:00"
  instance_class               = "m4.large"
  performance_insights_enabled = false
}

resource "aws_db_instance" "pass" {
  cluster_identifier           = "aurora-cluster-demo"
  availability_zones           = ["us-west-2a", "us-west-2b", "us-west-2c"]
  database_name                = "mydb"
  master_username              = "foo"
  master_password              = "bar"
  backup_retention_period      = 5
  preferred_backup_window      = "07:00-09:00"
  deletion_protection          = true
  instance_class               = "m4.large"
  performance_insights_enabled = true
}

resource "aws_rds_cluster_instance" "fail" {
  identifier         = "aurora-cluster-demo-${count.index}"
  cluster_identifier = aws_rds_cluster.default.id
  instance_class     = "db.r4.large"
  engine             = aws_rds_cluster.default.engine
  engine_version     = aws_rds_cluster.default.engine_version
}

resource "aws_rds_cluster_instance" "fail2" {
  identifier                   = "aurora-cluster-demo-${count.index}"
  cluster_identifier           = aws_rds_cluster.default.id
  instance_class               = "db.r4.large"
  engine                       = aws_rds_cluster.default.engine
  engine_version               = aws_rds_cluster.default.engine_version
  performance_insights_enabled = false
}

resource "aws_rds_cluster_instance" "pass" {
  identifier                   = "aurora-cluster-demo-${count.index}"
  cluster_identifier           = aws_rds_cluster.default.id
  instance_class               = "db.r4.large"
  engine                       = aws_rds_cluster.default.engine
  engine_version               = aws_rds_cluster.default.engine_version
  performance_insights_enabled = true
}