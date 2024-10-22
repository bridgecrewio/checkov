
resource "aws_dynamodb_table_replica" "pass" {
  provider         = "aws.alt"
  global_table_arn = aws_dynamodb_table.pass.arn
  kms_key_arn = aws_kms_key.test.arn

  tags = {
    Name = "taggy"
  }
}

resource "aws_dynamodb_table_replica" "fail" {
  provider         = "aws.alt"
  global_table_arn = aws_dynamodb_table.fail.arn

  tags = {
    Name = "taggy"
  }
}
