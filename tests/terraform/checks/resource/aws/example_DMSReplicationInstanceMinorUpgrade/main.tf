resource "aws_dms_replication_instance" "pass" {
  engine_version             = "3.1.4"
  multi_az                   = false
  publicly_accessible        = true
  replication_instance_class = "dms.t2.micro"
  replication_instance_id    = "test-dms-replication-instance-tf"
  kms_key_arn                = aws_kms_key.example.arn
  auto_minor_version_upgrade = true
}


resource "aws_dms_replication_instance" "fail" {
  engine_version             = "3.1.4"
  multi_az                   = false
  publicly_accessible        = true
  replication_instance_class = "dms.t2.micro"
  replication_instance_id    = "test-dms-replication-instance-tf"
  # kms_key_arn = ""
  auto_minor_version_upgrade = false
}