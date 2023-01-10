resource "aws_opensearch_domain" "os_fail_1" {
  domain_name    = "ggkitty"
  engine_version = "Elasticsearch_7.1"

  cluster_config {
    instance_type = "r5.large.search"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  node_to_node_encryption {
    enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
}

resource "aws_opensearch_domain" "os_fail_2" {
  domain_name    = "ggkitty"
  engine_version = "Elasticsearch_7.1"

  cluster_config {
    instance_type = "r5.large.search"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  node_to_node_encryption {
    enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
}

resource "aws_opensearch_domain" "os_pass" {
  domain_name    = "ggkitty"
  engine_version = "Elasticsearch_7.1"

  cluster_config {
    instance_type = "r5.large.search"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  encrypt_at_rest {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  node_to_node_encryption {
    enabled = true
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
}

resource "aws_elasticsearch_domain" "es_fail_1" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_elasticsearch_domain" "es_fail_2" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  advanced_security_options {
    enabled                        = false
    anonymous_auth_enabled         = true
    internal_user_database_enabled = false
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  tags = {
    Domain = "TestDomain"
  }
}

resource "aws_elasticsearch_domain" "es_pass" {
  domain_name           = "example"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "r4.large.elasticsearch"
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "example"
      master_user_password = "Barbarbarbar1!"
    }
  }

  tags = {
    Domain = "TestDomain"
  }
}