resource "aws_securitylake_subscriber" "fail" {
  subscriber_identity {
    # external_id is missing
    principal   = "arn:aws:iam::123456789012:role/some-role"
  }
  access_type = "LAKEFORMATION"
  source {
    aws_log_source_resource {
      source_name = "ROUTE53"
      source_version = "1.0"
    }
  }
}
