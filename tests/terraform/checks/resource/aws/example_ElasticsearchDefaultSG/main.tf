resource "aws_elasticsearch_domain" "pass" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  vpc_options {
    security_group_ids = ["sg_1234545"]
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
    enforce_https = true
  }

  vpc_options {
  }

  tags = {
    Domain = "TestDomain"
  }
}
