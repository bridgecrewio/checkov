# PASS case

resource "aws_elasticsearch_domain" "pass" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
    dedicated_master_enabled = true
  }

  tags = {
    Domain = "TestDomain"
  }
}

# FAIL case

resource "aws_elasticsearch_domain" "fail" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
    dedicated_master_enabled = false
  }

  tags = {
    Domain = "TestDomain"
  }
}