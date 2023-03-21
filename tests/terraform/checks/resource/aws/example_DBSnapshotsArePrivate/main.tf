resource "aws_db_snapshot" "pass" {
  db_instance_identifier = aws_db_instance.bar.id
  db_snapshot_identifier = "testsnapshot1234"
}

resource "aws_db_snapshot" "pass2" {
  db_instance_identifier = aws_db_instance.bar.id
  db_snapshot_identifier = "testsnapshot1234"
  shared_accounts=["680235478471"]
}

resource "aws_db_snapshot" "fail" {
  db_instance_identifier = aws_db_instance.bar.id
  db_snapshot_identifier = "testsnapshot1234"
  shared_accounts=["all"]
}