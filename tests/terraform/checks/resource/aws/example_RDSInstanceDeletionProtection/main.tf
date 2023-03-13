
resource "aws_db_instance" "fail" {
    cluster_identifier      = "aurora-cluster-demo"
    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
  database_name           = "mydb"
    master_username         = "foo"
    master_password         = "bar"
    backup_retention_period = 5
    preferred_backup_window = "07:00-09:00"
    deletion_protection = false
  instance_class            = "m4.large"
}

resource "aws_db_instance" "fail2" {
    cluster_identifier      = "aurora-cluster-demo"
    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
    database_name           = "mydb"
    master_username         = "foo"
    master_password         = "bar"
    backup_retention_period = 5
    preferred_backup_window = "07:00-09:00"
    instance_class            = "m4.large"
}

resource "aws_db_instance" "pass" {
    cluster_identifier      = "aurora-cluster-demo"
    availability_zones      = ["us-west-2a", "us-west-2b", "us-west-2c"]
    database_name           = "mydb"
    master_username         = "foo"
    master_password         = "bar"
    backup_retention_period = 5
    preferred_backup_window = "07:00-09:00"
    deletion_protection = true
    instance_class            = "m4.large"
}
