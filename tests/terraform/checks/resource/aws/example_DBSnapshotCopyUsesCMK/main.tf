resource "aws_db_snapshot_copy" "fail" {
  source_db_snapshot_identifier = aws_db_snapshot.example.db_snapshot_arn
  target_db_snapshot_identifier = "testsnapshot1234-copy"
}

resource "aws_db_snapshot_copy" "pass" {
  source_db_snapshot_identifier = aws_db_snapshot.example.db_snapshot_arn
  target_db_snapshot_identifier = "testsnapshot1234-copy"
  kms_key_id= aws_kms_key.example.id
}