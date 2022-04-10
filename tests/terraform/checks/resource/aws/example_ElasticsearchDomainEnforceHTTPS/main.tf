resource "aws_elasticsearch_domain" "pass" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_elasticsearch_domain" "pass2" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }
  domain_endpoint_options {
      enforce_https = true
  }
  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_elasticsearch_domain" "fail" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }
  domain_endpoint_options {
      enforce_https = false
  }
  tags = {
    Domain = "TestDomain"
  }
}