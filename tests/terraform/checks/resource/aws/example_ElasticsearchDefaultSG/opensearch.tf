resource "aws_opensearch_domain" "pass" {
  domain_name    = "example"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }
  encrypt_at_rest {
    enabled = true
  }

  vpc_options {
    security_group_ids = ["sg_1234545"]
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

  encrypt_at_rest {
    enabled = false
  }

  vpc_options {

  }

  tags = {
    Domain = "TestDomain"
  }
}
