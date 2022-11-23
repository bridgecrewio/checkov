resource "aws_redshiftserverless_namespace" "fail" {
  namespace_name = "test-fail-namespace"
}

resource "aws_redshiftserverless_namespace" "pass" {
  namespace_name = "test-pass-namespace"
  kms_key_id = aws_kms_key.example.arn
}
