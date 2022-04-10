# pass

resource "aws_elasticsearch_domain" "enabled" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }

  encrypt_at_rest {
    enabled = true
  }
}

# fail

resource "aws_elasticsearch_domain" "default" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }
}

resource "aws_elasticsearch_domain" "disabled" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }

  encrypt_at_rest {
    enabled = false
  }
}

