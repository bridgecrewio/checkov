resource "aws_elasticsearch_domain" "fail" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_elasticsearch_domain" "pass" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.example.arn
    log_type                 = "AUDIT_LOGS"
    enabled = true
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_cloudwatch_log_group" "example" {

}