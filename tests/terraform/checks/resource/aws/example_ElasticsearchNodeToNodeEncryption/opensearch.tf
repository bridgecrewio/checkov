# pass
resource "aws_opensearch_domain" "without_cluster_config" {
  domain_name = "without_cluster_config"
}

resource "aws_opensearch_domain" "without_instance_count" {
  domain_name = "without_instance_count"

  cluster_config {}
}

resource "aws_opensearch_domain" "instance_count_not_bigger_than_1" {
  domain_name = "instance_count_not_bigger_than_1"

  cluster_config {
    instance_count = 1 // a value <= 1
  }
}

resource "aws_opensearch_domain" "node_to_node_encryption_enabled" {
  domain_name = "node_to_node_encryption_enabled"

  cluster_config {
    instance_count = 2 // a value > 1
  }

  node_to_node_encryption {
    enabled = true
  }
}

resource "aws_opensearch_domain" "old_hcl" {
  domain_name = "old_hcl"

  cluster_config = {
    instance_count = 2
  }

  node_to_node_encryption = {
    enabled = true
  }
}

# fail
resource "aws_opensearch_domain" "node_to_node_encryption_disabled" {
  domain_name = "node_to_node_encryption_disabled"

  cluster_config {
    instance_count = 2 // a value > 1
  }

  node_to_node_encryption {
    enabled = false
  }
}

resource "aws_opensearch_domain" "node_to_node_encryption_doesnt_exist" {
  domain_name = "node_to_node_encryption_doesnt_exist"

  cluster_config {
    instance_count = 2 // a value > 1
  }
}

# unknown
resource "aws_opensearch_domain" "instance_count_not_number" {
  domain_name = "instance_count_not_number"

  cluster_config {
    instance_count = "not_int"
  }
}