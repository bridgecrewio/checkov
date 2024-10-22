resource "aws_dms_s3_endpoint" "fail" {
  endpoint_id             = "donnedtipi"
  endpoint_type           = "target"
  bucket_name             = "beckut_name"
  service_access_role_arn = aws_iam_role.example.arn

  depends_on = [aws_iam_role_policy.example]
}

resource "aws_dms_s3_endpoint" "fail2" {
  endpoint_id             = "donnedtipi"
  endpoint_type           = "target"
  bucket_name             = "beckut_name"
  service_access_role_arn = aws_iam_role.example.arn

  kms_key_arn=""
  depends_on = [aws_iam_role_policy.example]
}

resource "aws_dms_s3_endpoint" "pass" {
  endpoint_id             = "donnedtipi"
  endpoint_type           = "target"
  bucket_name             = "beckut_name"
  service_access_role_arn = aws_iam_role.example.arn

  kms_key_arn="arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  depends_on = [aws_iam_role_policy.example]
}

resource "aws_dms_s3_endpoint" "pass2" {
  endpoint_id             = "donnedtipi"
  endpoint_type           = "target"
  bucket_name             = "beckut_name"
  service_access_role_arn = aws_iam_role.example.arn

  kms_key_arn=aws-kms_key.pike.arn
  depends_on = [aws_iam_role_policy.example]
}