variable "extra_statements_pass" {
  type    = list(any)
  default = [
    "{Effect = \"Allow\", Principal = \"*\"}",
  ]
}

resource "aws_s3_bucket_policy" "concat_mixed_pass" {
  bucket = "example"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Sid       = "DenyInsecureTransport"
          Effect    = "Deny"
          Principal = "*"
          Action    = "s3:*"
          Resource  = "*"
          Condition = { Bool = { "aws:SecureTransport" = "false" } }
        },
      ],
      var.extra_statements_pass,
    )
  })
}
