resource "aws_opensearch_domain" "pass" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }
    encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https=true
  }
  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_opensearch_domain" "fail" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }

  domain_endpoint_options {
    enforce_https=false
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_opensearch_domain" "pass2" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }

  tags = {
    Domain = "TestDomain"
  }
}