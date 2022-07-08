resource "aws_codeartifact_domain" "fail" {
  domain = "example"
  # encryption_key =
  tags = {
    "key" = "value"
  }
}

resource "aws_codeartifact_domain" "pass" {
  domain         = "example"
  encryption_key = aws_kms_key.example.arn
  tags = {
    "key" = "value"
  }
}
