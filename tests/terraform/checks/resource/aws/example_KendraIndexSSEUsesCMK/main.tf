resource "aws_kendra_index" "fail" {
  name        = "example"
  description = "example"
  edition     = "DEVELOPER_EDITION"
  role_arn    = aws_iam_role.this.arn

  tags = {
    "Key1" = "Value1"
  }
}

resource "aws_kendra_index" "pass" {
  name     = "example"
  role_arn = aws_iam_role.this.arn

  server_side_encryption_configuration {
    kms_key_id = data.aws_kms_key.this.arn
  }
}
