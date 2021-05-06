resource "aws_elasticsearch_domain" "missing" {
  domain_name           = "cloudrail-non-enc-in-tran"
  elasticsearch_version = "6.0"

  cluster_config {
    instance_type = "i3.large.elasticsearch"
  }

}

resource "aws_elasticsearch_domain" "pass" {
  domain_name           = var.es_domain
  elasticsearch_version = var.es_version

  advanced_security_options {
    enabled = var.advanced_security_options
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.examplea.arn
    log_type                 = var.log_publishing_options_type
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  cluster_config {
    instance_type            = var.instance_type
    instance_count           = var.instance_count
    dedicated_master_enabled = var.dedicated_master_enabled
    dedicated_master_count   = var.dedicated_master_count
    dedicated_master_type    = var.dedicated_master_type
    zone_awareness_enabled   = var.es_zone_awareness
    zone_awareness_config {
      availability_zone_count = 2
    }

    warm_enabled = false
    warm_count = 2
    warm_type  = "ultrawarm1.medium.elasticsearch"
  }

  vpc_options {
    subnet_ids = var.subnets
    security_group_ids = [
      aws_security_group.examplea.id
    ]
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.ebs_volume_size
    volume_type = var.ebs_volume_type
  }

  snapshot_options {
    automated_snapshot_start_hour = var.snapshot_start_hour
  }

  encrypt_at_rest {
    enabled = true
    kms_key_id = var.kms_key_id
  }

  node_to_node_encryption {
    enabled = true
  }

  tags = var.common_tags
}

resource "aws_elasticsearch_domain" "fail" {
  domain_name           = var.es_domain
  elasticsearch_version = var.es_version


  advanced_options = {
  }

  advanced_security_options {
    enabled = var.advanced_security_options  
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.examplea.arn
    log_type                 = var.log_publishing_options_type
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  cluster_config {
    instance_type            = var.instance_type
    instance_count           = var.instance_count
    dedicated_master_enabled = var.dedicated_master_enabled
    dedicated_master_count   = var.dedicated_master_count
    dedicated_master_type    = var.dedicated_master_type
    zone_awareness_enabled   = var.es_zone_awareness
    zone_awareness_config {
      availability_zone_count = 2
      // Number of Availability Zones for the domain to use with zone_awareness_enabled. Defaults to 2. Valid values: 2 or 3.

    }

    warm_enabled = false
    //2-150
    warm_count = 2
    warm_type  = "ultrawarm1.medium.elasticsearch"
  }

  vpc_options {
    subnet_ids = var.subnets
    security_group_ids = [
      aws_security_group.examplea.id
    ]
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.ebs_volume_size
    volume_type = var.ebs_volume_type
  }

  snapshot_options {
    automated_snapshot_start_hour = var.snapshot_start_hour
  }

  encrypt_at_rest {
    enabled = true
    //default is aws/es
    kms_key_id = var.kms_key_id
  }

  //add check 
  node_to_node_encryption {
    enabled = false
  }


  tags = var.common_tags
}