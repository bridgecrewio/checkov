provider "aws" {
  region = "eu-west-2"
}

resource "aws_elasticsearch_domain" "fail" {
  domain_name = "nodetonode"
  domain_endpoint_options {
    enforce_https       = false
    tls_security_policy = "Policy-Min-TLS-1-0-2019-07"
  }

  cluster_config {
    instance_count = 2
  }

  encrypt_at_rest {
    enabled = false
  }

  node_to_node_encryption {
    enabled = false
  }
}

resource "aws_elasticsearch_domain" "notset" {
  domain_name = "notset"

  cluster_config {
    instance_count = 2 // a value > 1
  }

  encrypt_at_rest {
    enabled = false
  }

  node_to_node_encryption {
    enabled = false
  }
}

resource "aws_elasticsearch_domain" "pass" {
  domain_name = "pass"

  domain_endpoint_options {
    enforce_https       = false
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  cluster_config {
    instance_count = 2
  }

  encrypt_at_rest {
    enabled = false
  }

  node_to_node_encryption {
    enabled = false
  }
}

resource "aws_elasticsearch_domain" "pass2" {
  domain_name = "pass2"

  domain_endpoint_options {
    enforce_https       = false
    tls_security_policy = "Policy-Min-TLS-1-2-PFS-2023-10"
  }

  cluster_config {
    instance_count = 2
  }

  encrypt_at_rest {
    enabled = false
  }

  node_to_node_encryption {
    enabled = false
  }
}
