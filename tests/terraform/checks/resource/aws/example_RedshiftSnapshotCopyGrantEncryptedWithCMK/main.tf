resource "aws_redshift_snapshot_copy_grant" "pass" {
  snapshot_copy_grant_name = "my-grant"
  kms_key_id               = aws_kms_key.test.arn
}

resource "aws_redshift_snapshot_copy_grant" "fail" {
  snapshot_copy_grant_name = "my-grant"
}