

resource "aws_elasticsearch_domain" "fail2" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }

  encrypt_at_rest {
    enabled = true
  }
}


resource "aws_elasticsearch_domain" "fail" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }
}

resource "aws_elasticsearch_domain" "pass" {
  domain_name = "example"

  cluster_config {
    instance_type = "r5.large.elasticsearch"
  }

  encrypt_at_rest {
    kms_key_id = aws_kms_key.example.arn
  }
}
