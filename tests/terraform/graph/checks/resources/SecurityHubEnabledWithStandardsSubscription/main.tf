resource "aws_securityhub_account" "pass" {}

resource "aws_securityhub_standards_subscription" "pass" {
  depends_on    = [aws_securityhub_account.pass]
  standards_arn = "arn:aws:securityhub:us-east-1::ruleset/cis-aws-foundations-benchmark/v/1.2.0"
}

resource "aws_securityhub_account" "fail_no_subscription" {}
