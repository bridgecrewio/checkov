
resource "aws_opensearch_domain" "fail" {
  domain_name    = var.domain
  engine_version = "Elastisearch_7.10"

  cluster_config {
    instance_type = "m4.large.search"
  }
}

resource "aws_opensearch_domain" "pass" {
  domain_name    = var.domain
  engine_version = "Elastisearch_7.10"

  cluster_config {
    instance_type = "m4.large.search"
  }

  vpc_options {
    subnet_ids = [
      data.aws_subnet_ids.selected.ids[0],
      data.aws_subnet_ids.selected.ids[1],
    ]

    security_group_ids = [aws_security_group.es.id]
  }

}
