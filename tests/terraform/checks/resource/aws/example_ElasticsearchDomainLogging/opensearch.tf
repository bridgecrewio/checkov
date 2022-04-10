resource "aws_opensearch_domain" "fail" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_opensearch_domain" "pass" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.example.arn
    log_type                 = "INDEX_SLOW_LOGS"
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_opensearch_domain" "pass2" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.example.arn
    log_type                 = "INDEX_SLOW_LOGS"
    enabled=true
  }
  cluster_config {
    instance_type = "r4.large.search"
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_opensearch_domain" "fail2" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.example.arn
    log_type                 = "INDEX_SLOW_LOGS"
    enabled=false
  }
  cluster_config {
    instance_type = "r4.large.search"
  }

  tags = {
    Domain = "TestDomain"
  }
}