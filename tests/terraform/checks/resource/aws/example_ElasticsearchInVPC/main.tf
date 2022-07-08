
resource "aws_elasticsearch_domain" "fail" {
  domain_name           = var.domain
  elasticsearch_version = "6.3"

  cluster_config {
    instance_type = "m4.large.elasticsearch"
  }
}

resource "aws_elasticsearch_domain" "pass" {
  domain_name           = var.domain
  elasticsearch_version = "6.3"

  cluster_config {
    instance_type = "m4.large.elasticsearch"
  }

  vpc_options {
    subnet_ids = [
      data.aws_subnet_ids.selected.ids[0],
      data.aws_subnet_ids.selected.ids[1],
    ]

    security_group_ids = [aws_security_group.es.id]
  }

}
