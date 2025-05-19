provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"  # checkov:skip=CKV_SECRET_2 test secret
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # checkov:skip=CKV_SECRET_6 test secret
}
resource "azurerm_virtual_machine" "main" {
  name                = "${var.prefix}-vm"
  location            = "${azurerm_resource_group.main.location}"
  resource_group_name = "${azurerm_resource_group.main.name}"
  network_interface_ids = [
  "${azurerm_network_interface.main.id}"]
  vm_size = "Standard_DS1_v2"

  # Uncomment this line to delete the OS disk automatically when deleting the VM
  # delete_os_disk_on_termination = true


  # Uncomment this line to delete the data disks automatically when deleting the VM
  # delete_data_disks_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
  storage_os_disk {
    name              = "myosdisk1"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }
  os_profile {
    computer_name  = "hostname"
    admin_username = "testadmin"
    admin_password = "Password1234!"  # checkov:skip=CKV_SECRET_80 test secret
  }
  os_profile_linux_config {
    disable_password_authentication = false
  }
  tags = {
    environment = "staging"
  }
}

resource "azurerm_managed_disk" "source" {
  encryption_settings {
    enabled = false
  }
  create_option        = ""
  location             = ""
  name                 = ""
  resource_group_name  = "foo"
  storage_account_type = ""
}

resource "google_storage_bucket" "with-customer-encryption-key" {
  name     = "customer-managed-encryption-key-bucket-${data.google_project.current.number}"
  location = "EU"


}


resource "aws_s3_bucket" "foo-bucket" {
  region        = var.region
  bucket        = local.bucket_name
  acl           = "public-read"
  force_destroy = true

  tags = {
    Name = "foo-${data.aws_caller_identity.current.account_id}"
  }
  #checkov:skip=CKV_AWS_20:The bucket is a public static content host
  versioning {
    enabled = true
  }
}
data "aws_caller_identity" "current" {}

resource "google_sql_database_instance" "gcp_sql_db_instance_bad" {
  settings {
    tier = "1"
  }
}

resource "google_sql_database_instance" "gcp_sql_db_instance_good" {
  settings {
    tier = "1"
    ip_configuration {
      require_ssl = "True"
    }
  }
}

resource "google_container_cluster" "primary_good" {
  name               = "google_cluster"
  enable_legacy_abac = false
  resource_labels {
    Owner = "SomeoneNotWorkingHere"
  }

  node_config {
    image_type = "cos"
  }

  ip_allocation_policy {}

  private_cluster_config {}
}

resource "google_container_cluster" "primary_good2" {
  name               = "google_cluster"
  monitoring_service = "monitoring.googleapis.com"

  master_authorized_networks_config {}

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  node_config {
    image_type = "not-cos"
  }

  pod_security_policy_config {
    enabled = true
  }

  private_cluster_config {}
}

resource "google_container_cluster" "primary_bad" {
  name               = "google_cluster_bad"
  monitoring_service = "none"
  enable_legacy_abac = true

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block = "0.0.0.0/0"
      display_name = "The world"
    }
  }

  master_auth {
    username = "test"
    password = "password"
  }

  resource_labels {}
}

resource "google_container_node_pool" "bad_node_pool" {
  cluster = ""
  management {
  }
}

resource "google_container_node_pool" "good_node_pool" {
  cluster = ""
  management {
    auto_repair = true
  }
}

resource "aws_kms_key" "my_kms_key" {
  description         = "My KMS Key"
  enable_key_rotation = true
}

resource "aws_iam_account_password_policy" "password-policy" {
  minimum_password_length        = 15
  require_lowercase_characters   = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_symbols                = true
  allow_users_to_change_password = true
}

resource "aws_iam_account_password_policy" "paswword-policy_example_with_string_values" {
  allow_users_to_change_password = var.allow_users_to_change_password
  hard_expiry                    = var.hard_expiry
  minimum_password_length        = "14"
  max_password_age               = "40"
  password_reuse_prevention      = "3"
  require_lowercase_characters   = var.require_lowercase_characters
  require_uppercase_characters   = var.require_uppercase_characters
  require_numbers                = var.require_numbers
  require_symbols                = var.require_symbols
}

resource "aws_security_group" "bar-sg" {
  name   = "sg-bar"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    security_groups = [
    aws_security_group.foo-sg.id]
    description = "foo"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = [
    "0.0.0.0/0"]
  }

}

resource "aws_security_group" "ingress_as_map" {
  name        = "${var.name}_elasticsearch"
  description = "ELK ${var.name} ElasticSearch instances"
  vpc_id      = "${data.aws_vpc.selected.id}"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress = {
    from_port       = 9200
    to_port         = 9200
    protocol        = "tcp"
    security_groups = ["${aws_security_group.elk_logstash.id}"]
  }

  ingress = {
    from_port       = 9300
    to_port         = 9400
    protocol        = "tcp"
    security_groups = ["${aws_security_group.elk_kibana.id}"]
    self            = true
  }

  ingress = {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = "${concat(list(aws_security_group.elk_admin.id), var.admin_sg_ids)}"
    cidr_blocks     = "${var.admin_cidrs}"
  }

  tags = "${merge(var.tags, map("Module", var.module))}"
}

resource "aws_iam_policy" "example" {
  name   = "example_policy"
  path   = "/"
  policy = "${data.aws_iam_policy_document.example.json}"
}

resource "aws_elasticache_replication_group" "example" {
  automatic_failover_enabled = true
  availability_zones = [
    "us-west-2a",
  "us-west-2b"]
  replication_group_id          = "tf-rep-group-1"
  replication_group_description = "test description"
  node_type                     = "cache.m4.large"
  number_cache_clusters         = 2
  parameter_group_name          = "default.redis3.2"
  port                          = 6379
  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = true
  auth_token                    = var.auth_token
}

resource "aws_ecr_repository_policy" "public_repo_policy" {
  repository = "public_repo"

  policy = <<EOF
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:DescribeRepositories",
                "ecr:GetRepositoryPolicy",
                "ecr:ListImages",
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ]
        }
    ]
}
EOF
}

resource "aws_ecr_repository" "foo" {
  name                 = "bar"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository_policy" "private_repo_policy" {
  repository = "private_repo"

  policy = <<EOF
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "new policy",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::123456789012:user/pull-user-1",
                    "arn:aws:iam::123456789012:user/pull-user-2"
                ]
            },
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:DescribeRepositories",
                "ecr:GetRepositoryPolicy",
                "ecr:ListImages",
                "ecr:DeleteRepository",
                "ecr:BatchDeleteImage",
                "ecr:SetRepositoryPolicy",
                "ecr:DeleteRepositoryPolicy"
            ]
        }
    ]
}
EOF
}

resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = "${aws_s3_bucket.b.bucket_regional_domain_name}"
    origin_id   = "${local.s3_origin_id}"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/ABCDEFG1234567"
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Some comment"
  default_root_object = "index.html"

  logging_config {
    include_cookies = false
    bucket          = "mylogs.s3.amazonaws.com"
    prefix          = "myprefix"
  }

  aliases = [
    "mysite.example.com",
  "yoursite.example.com"]

  ordered_cache_behavior {
    path_pattern = "/content/immutable/*"
    allowed_methods = [
      "GET",
      "HEAD",
    "OPTIONS"]
    cached_methods = [
      "GET",
      "HEAD",
    "OPTIONS"]
    target_origin_id = "${local.s3_origin_id}"

    forwarded_values {
      query_string = false
      headers = [
      "Origin"]

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  # Cache behavior with precedence 1
  ordered_cache_behavior {
    path_pattern = "/content/*"
    allowed_methods = [
      "GET",
      "HEAD",
    "OPTIONS"]
    cached_methods = [
      "GET",
    "HEAD"]
    target_origin_id = "${local.s3_origin_id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

dynamic "ordered_cache_behavior" {
    for_each = var.ordered_cache

    content {
      path_pattern = ordered_cache_behavior.value.path_pattern

      allowed_methods  = ordered_cache_behavior.value.allowed_methods
      cached_methods   = ordered_cache_behavior.value.cached_methods
      target_origin_id = module.distribution_label.id
      compress         = ordered_cache_behavior.value.compress
      trusted_signers  = var.trusted_signers

      forwarded_values {
        query_string = ordered_cache_behavior.value.forward_query_string
        headers      = ordered_cache_behavior.value.forward_header_values

        cookies {
          forward = ordered_cache_behavior.value.forward_cookies
        }
      }

      viewer_protocol_policy = ordered_cache_behavior.value.viewer_protocol_policy
      default_ttl            = ordered_cache_behavior.value.default_ttl
      min_ttl                = ordered_cache_behavior.value.min_ttl
      max_ttl                = ordered_cache_behavior.value.max_ttl

      dynamic "lambda_function_association" {
        for_each = ordered_cache_behavior.value.lambda_function_association
        content {
          event_type   = lambda_function_association.value.event_type
          include_body = lookup(lambda_function_association.value, "include_body", null)
          lambda_arn   = lambda_function_association.value.lambda_arn
        }
      }
    }
  }

  price_class = "PriceClass_200"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations = [
        "US",
        "CA",
        "GB",
      "DE"]
    }
  }

  tags = {
    Environment = "production"
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  default_cache_behavior {
    allowed_methods = [
      "DELETE",
      "GET",
      "HEAD",
      "OPTIONS",
      "PATCH",
      "POST",
    "PUT"]
    cached_methods = [
      "GET",
    "HEAD"]
    target_origin_id = "${local.s3_origin_id}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }
}

resource "aws_iam_user_policy_attachment" "test-attach" {
  user       = "${aws_iam_user.user.name}"
  policy_arn = "${aws_iam_policy.policy.arn}"
}
resource "aws_iam_policy_attachment" "test-attach" {
  name = "test-attachment"
  users = [
  "${aws_iam_user.user.name}"]
  roles = [
  "${aws_iam_role.role.name}"]
  groups = [
  "${aws_iam_group.group.name}"]
  policy_arn = "${aws_iam_policy.policy.arn}"
}

resource "aws_iam_user_policy" "lb_ro" {
  name = "test"
  user = "${aws_iam_user.lb.name}"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:Describe*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_s3_bucket" "bridgecrew_cws_bucket" {
  count = var.existing_bucket_name == null ? 1 : 0

  bucket = local.bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "Delete old log files"
    enabled = true

    noncurrent_version_expiration {
      days = var.log_file_expiration
    }

    expiration {
      days = var.log_file_expiration
    }
  }

  dynamic "logging" {
    for_each = var.logs_bucket_id != null ? [var.logs_bucket_id] : []

    content {
      target_bucket = logging.value
      target_prefix = "/${local.bucket_name}"
    }
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = local.kms_key
        sse_algorithm     = "aws:kms"
      }
    }
  }

  tags = {
    Name = "BridgecrewCWSBucket"
  }
}

resource "aws_s3_bucket" "dynamic_sse_block_string" {
  count = local.using_existing_origin ? 0 : 1
  bucket = module.origin_label.id
  acl = "private"
  tags = module.origin_label.tags
  force_destroy = var.origin_force_destroy
  region = data.aws_region.current.name

  dynamic "server_side_encryption_configuration" {
    for_each = var.encryption_enabled ? [
      "true"] : []

    content {
      rule {
        apply_server_side_encryption_by_default {
          sse_algorithm = "AES256"
        }
      }
    }
  }
}

resource "aws_s3_bucket" "sse_block_and_rule_block_as_map" {
  bucket = "${var.bucket_name}"
  policy = "${data.aws_iam_policy_document.iam_policy_document_s3.json}"

  versioning = {
    enabled = true
  }

  lifecycle = {
    prevent_destroy = true
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_efs_file_system" "sharedstore" {
  creation_token                  = "my-product"

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

    kms_key_id                      = "aws/efs"
    encrypted                       = true
    performance_mode                = "generalPurpose"
    provisioned_throughput_in_mibps = 0
    throughput_mode                 = "bursting"

}

resource "aws_instance" "compute_host" {
# ec2 have plain text secrets in user data
ami           = "ami-04169656fea786776"
instance_type = "t2.nano"
user_data     = <<EOF
#! /bin/bash
sudo apt-get update
sudo apt-get install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
export AWS_ACCESS_KEY_ID
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_DEFAULT_REGION=us-west-2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
EOF
tags = {
Name  = "${local.resource_prefix.value}-ec2"
}
}

data aws_iam_policy_document "bad_policy_document" {
  version = "2012-10-17"
  statement {
    actions = ["*"]
    resources = ["*"]
  }
}

data aws_iam_policy_document "good_policy_document" {
  version = "2012-10-17"
  statement {
    actions = ["s3:Get*"]
    resources = ["*"]
    effect = "Allow"
  }
}

data aws_iam_policy_document "long_bad_policy_document" {
  version = "2012-10-17"
  statement {
    actions = ["s3:Get*"]
    resources = ["*"]
    effect = "Allow"
  }
  statement {
    actions = ["*"]
    resources = ["*"]
    effect = "Allow"
  }
}

data aws_iam_policy_document "good_deny_policy_document" {
  version = "2012-10-17"
  statement {
    actions = ["*"]
    resources = ["*"]
    effect = "Deny"
    condition {
      test = "ArnLike"
      values = ["arn:aws:mock:mock:mock"]
      variable = "aws:mock"
    }
  }
}

data aws_iam_policy_document "scp_deny_example" {
  statement {
    sid    = "NoIAMUsers"
    effect = "Deny"
    not_actions = [
      "iam:Get*",
      "iam:List*",
      "iam:Describe*",
    ]
    resources = [
      "arn:aws:iam::*:user/*",
    ]
  }
}

resource aws_lambda_function "good-function" {
  filename      = "lambda_function_payload.zip"
  function_name = "good_lambda_function_name"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "exports.test"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = "${filebase64sha256("lambda_function_payload.zip")}"

  runtime = "nodejs12.x"
  environment {
    variables = "${var.variables_map}"
  }
}

resource aws_lambda_function "bad-function" {
  filename = "lambda_function_payload.zip"
  function_name = "bad_lambda_function_name"
  role = "${aws_iam_role.iam_for_lambda.arn}"
  handler = "exports.test"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = "${filebase64sha256("lambda_function_payload.zip")}"

  runtime = "nodejs12.x"
  environment {
    variables = {
      AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
      secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # checkov:skip=CKV_SECRET_80 test secret
    }
  }
}

resource "aws_lambda_function" "block_environment_variables" {

  filename = "${path.module}/canary_sensor_api_capture.zip"
  description = "A lambda that reaches out to the Canary API used on the Canary website, obtains bearer tokens for communication, gets a list of the devices attached to the account, and fetches the sensor data for those devices."
  function_name = "canary_sensor_api_capture"
  role = "${aws_iam_role.canary_sensor_api_capture_role.arn}"
  handler = "canary_sensor_api_capture.lambda_handler"
  source_code_hash = "${data.archive_file.canary_sensor_api_capture_zip.output_base64sha256}"
  runtime = "python2.7"
  timeout = 10

  environment {

    variables {

      kmsArn = "${var.kms_arn}"
      username = "${var.canary_username}"
      password = "${var.canary_encrytped_password}"
    }
  }
}

resource "aws_lambda_function" "environment_and_variables_map" {
  filename         = "${data.archive_file.ami_backup.output_path}"
  function_name    = "${module.label_backup.id}"
  description      = "Automatically backup EC2 instance (create AMI)"
  role             = "${aws_iam_role.ami_backup.arn}"
  timeout          = 60
  handler          = "ami_backup.lambda_handler"
  runtime          = "python2.7"
  source_code_hash = "${data.archive_file.ami_backup.output_base64sha256}"

  environment = {
    variables = {
      region                = "${var.region}"
      ami_owner             = "${var.ami_owner}"
      instance_id           = "${var.instance_id}"
      retention             = "${var.retention_days}"
      label_id              = "${module.label.id}"
      reboot                = "${var.reboot ? "1" : "0"}"
      block_device_mappings = "${jsonencode(var.block_device_mappings)}"
    }
  }
}

resource "aws_lambda_function" "dynamic_environment_example" {
  function_name = var.name
  filename = "${path.module}/lambda_function.zip"
  role = aws_iam_role.this.arn
  handler = var.handler
  runtime = var.runtime
  memory_size = var.memory_size
  timeout = var.timeout
  layers = var.layers
  description = var.description
  reserved_concurrent_executions = var.reserved_concurrent_executions
  publish = var.publish
  kms_key_arn = var.kms_key_arn

  dynamic "environment" {
    for_each = length(var.environment_variables) > 0 ? [
      true] : []

    content {
      variables = var.environment_variables
    }
  }
}
resource "aws_s3_bucket" "versioning-string" {
  bucket = "${var.bucket}"
  region = "${var.region}"
  acl    = "${var.acl}"

  cors_rule = "${var.cors_rule}"
  website   = "${var.website}"

  force_destroy = "${var.force_destroy}"

  lifecycle_rule = "${var.lifecycle_rule}"
  versioning     = "${var.versioning}"
  logging        = "${var.logging}"

  request_payer                        = "${var.request_payer}"
  replication_configuration            = "${var.replication_configuration}"
  server_side_encryption_configuration = "${var.server_side_encryption_configuration}"

  tags = "${var.tags}"
}

resource aws_eks_cluster "eks_bad" {
  name = "bad-eks"
  role_arn = var.role_arn
  vpc_config {
    subnet_ids = []
    endpoint_public_access = true
  }


  encryption_config {
    provider {
      key_arn = var.key_arn
    }
    resources = []
  }
}

resource aws_eks_cluster "eks_bad2" {
  name = "bad-eks2"
  role_arn = var.role_arn
  vpc_config {
    subnet_ids = []
    endpoint_public_access = true
  }
}

resource aws_eks_cluster "eks_good" {
  name = "good-eks2"
  role_arn = var.role_arn
  vpc_config {
    subnet_ids = []
    endpoint_public_access = true
  }

  encryption_config {
    provider {
      key_arn = var.key_arn
    }
    resources = ["secrets"]
  }
}

resource azurerm_kubernetes_cluster "example" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  agent_pool_profile {}
  service_principal {}

  api_server_authorized_ip_ranges = ["192.168.0.0/16"]

  tags = {
    Environment = "Production"
  }

  addon_profile {
    kube_dashboard {
      enabled = true
    }

    oms_agent {
      enabled = true
      log_analytics_workspace_id = ""
    }
  }
}

resource azurerm_kubernetes_cluster "bad-example" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  agent_pool_profile {}
  service_principal {}

  api_server_authorized_ip_ranges = []

  role_based_access_control {
    enabled = true
  }

  network_profile {
    network_plugin = "azure"
  }

  tags = {
    Environment = "Production"
  }
}

resource azurerm_kubernetes_cluster "bad-example" {
  name                = "example-aks1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  agent_pool_profile {}
  service_principal {}

  role_based_access_control {
    enabled = false
  }

  addon_profile {
    kube_dashboard {
      enabled = false
    }
  }

  network_profile {
    network_plugin = "azure"
    network_policy = "network_policy"
  }

  tags = {
    Environment = "Production"
  }
}


resource "aws_elasticsearch_domain" "dynamic_cluster_config_example" {
  domain_name = var.domain_name
  elasticsearch_version = var.elasticsearch_version
  access_policies = var.access_policies
  advanced_options = var.advanced_options == null ? {} : var.advanced_options
  dynamic "cluster_config" {
    for_each = local.cluster_config
    content {
      instance_type = lookup(cluster_config.value, "instance_type")
      instance_count = lookup(cluster_config.value, "instance_count")
      dedicated_master_enabled = lookup(cluster_config.value, "dedicated_master_enabled")
      dedicated_master_type = lookup(cluster_config.value, "dedicated_master_type")
      dedicated_master_count = lookup(cluster_config.value, "dedicated_master_count")
      zone_awareness_enabled = lookup(cluster_config.value, "zone_awareness_enabled")
    }
  }
}

resource "aws_api_gateway_method" "apigateway_method_with_authorization" {
  rest_api_id   = "${var.rest_api_id}"
  resource_id   = "${var.resource_id}"
  http_method   = "OPTIONS}"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_method" "apigateway_method_no_authorization" {
  rest_api_id   = var.api_id
  resource_id   = var.api_resource_id
  http_method   = var.http_method
  authorization = "NONE"
}

resource "aws_iam_role" "example_with_specific_service" {
  name = "${var.name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role" "example_with_no_specific_service_attached" {
  name = "${var.name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "AWS": "*"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "json_bad_policy" {
  name = "test_policy"
  role = aws_iam_role.test_role.id

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "*"
        ],
        "Effect": "Allow",
        "Resource": "*"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy" "json_good_policy" {
  name = "test_policy"
  role = aws_iam_role.test_role.id

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "ec2:Describe*"
        ],
        "Effect": "Allow",
        "Resource": "*"
      }
    ]
  }
  EOF
}

resource "aws_iam_role" "example_1_allowing_all_aws_principals" {
  name = "${var.name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "AWS": "123123123123"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role" "example_2_allowing_all_aws_principals" {
  name = "${var.name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "AWS": "arn:aws:iam::123123123123:root"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "google_compute_subnetwork" "subnet-without-logging" {
          name          = "log-test-subnetwork"
          ip_cidr_range = "10.2.0.0/16"
          region        = "us-central1"
          network       = google_compute_network.custom-test.id
        }

resource "google_compute_subnetwork" "subnet-with-logging" {
          name          = "log-test-subnetwork"
          ip_cidr_range = "10.2.0.0/16"
          region        = "us-central1"
          network       = google_compute_network.custom-test.id

          log_config {
            aggregation_interval = "INTERVAL_10_MIN"
            flow_sampling        = 0.5
            metadata             = "INCLUDE_ALL_METADATA"
          }
        }

resource "google_compute_ssl_policy" "modern-profile-without-min-tls" {
  name    = "production-ssl-policy"
  profile = "MODERN"
}

resource "google_compute_ssl_policy" "modern-profile-with-min-tls" {
  name            = "nonprod-ssl-policy"
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
}

resource "google_compute_ssl_policy" "custom-profile" {
  name            = "custom-ssl-policy"
  min_tls_version = "TLS_1_2"
  profile         = "CUSTOM"
  custom_features = ["TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384", "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"]
}

resource "google_project" "default-network-created" {
  name       = "My Project"
  project_id = "your-project-id"
  org_id     = "1234567"
}

resource "google_project" "no-default-network-created" {
  name       = "My Project"
  project_id = "your-project-id"
  org_id     = "1234567"
  auto_create_network = false
}

resource "google_storage_bucket_iam_member" "member-not-public" {
  bucket = google_storage_bucket.default.name
  role = "roles/storage.admin"
  member = "user:jane@example.com"
}

resource "google_storage_bucket_iam_binding" "binding-with-public-member" {
  bucket = google_storage_bucket.default.name
  role = "roles/storage.admin"
  members = [
    "allAuthenticatedUsers"
  ]
}

resource "google_storage_bucket" "bucket-with-uniform-access-enabled" {
  name          = "image-store.com"
  location      = "EU"
  force_destroy = true

  bucket_policy_only = true

  }

resource "google_compute_instance" "bad-example" {
name         = "test"
machine_type = "n1-standard-1"
zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
  }
  metadata = {
    enable-oslogin = false
    serial-port-enable = true
              }
  can_ip_forward = true
  boot_disk {}
  network_interface {}
}

resource "google_compute_instance" "good-example" {
name         = "test"
machine_type = "n1-standard-1"
zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email = "example@email.com"
  }
  metadata = {
       block-project-ssh-keys = true
              }
  boot_disk {
    disk_encryption_key_raw = "acXTX3rxrKAFTF0tYVLvydU1riRZTvUNC4g5I11NY-c="
  }
  shielded_instance_config {}
  network_interface {}
}

resource "google_compute_project_metadata" "good-example" {
  metadata = {
    foo  = "bar"
    enable-oslogin = true
  }
}

resource "google_compute_project_metadata" "bad-example" {
  metadata = {
    foo  = "bar"
    enable-oslogin = true
  }
}

resource "google_compute_disk" "good_example" {
  name  = "test-disk"
  type  = "pd-ssd"
  zone  = "us-central1-a"
  image = "debian-8-jessie-v20170523"
  physical_block_size_bytes = 4096
  disk_encryption_key {
    raw_key = "acXTX3rxrKAFTF0tYVLvydU1riRZTvUNC4g5I11NY-c="
    }
}

resource "google_project_iam_member" "bad-role" {
    project = "your-project-id"
    role    = "roles/iam.serviceAccountUser"
    member  = "user:jane@example.com"
}

resource "google_project_iam_binding" "bad-role" {
  project = "your-project-id"
  role    = "roles/iam.serviceAccountTokenCreator"

  members = [
    "user:jane@example.com",
  ]
}

resource "google_project_iam_member" "admin-user-managed-member" {
  project = "your-project-id"
  role    = "roles/owner"
  member  = "user:user@123456789.iam.gserviceaccount.com"
}

resource "google_kms_crypto_key" "good-rotation-period" {
  name            = "crypto-key-example"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = "90d"
  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_network_security_rule" "inbound-rdp" {
  name                        = "test123"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "TCP"
  source_port_range           = "*"
  destination_port_range      = "3389"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.example.name
  network_security_group_name = azurerm_network_security_group.example.name
}

resource "azurerm_network_security_rule" "inbound-ssh" {
  name                        = "test123"
  priority                    = 100
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "TCP"
  source_port_range           = "*"
  destination_port_range      = "22"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = azurerm_resource_group.example.name
  network_security_group_name = azurerm_network_security_group.example.name
}

resource "azurerm_mysql_firewall_rule" "open-to-internet" {
  name                = "office"
  resource_group_name = azurerm_resource_group.example.name
  server_name         = azurerm_mysql_server.example.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "255.255.255.255"
}

resource "azurerm_network_watcher_flow_log" "good-retention-policy" {
network_watcher_name = azurerm_network_watcher.test.name
resource_group_name  = azurerm_resource_group.test.name
network_security_group_id = azurerm_network_security_group.test.id
storage_account_id        = azurerm_storage_account.test.id
enabled                   = true

retention_policy {
  enabled = true
  days    = 90
}
}

resource "azurerm_app_service" "good-example" {
  name                = "example-app-service"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  app_service_plan_id = azurerm_app_service_plan.example.id
  https_only          = true
  client_cert_enabled = true

  auth_settings {
    enabled                       = true
    issuer                        = "https://sts.windows.net/d13958f6-b541-4dad-97b9-5a39c6b01297"
    default_provider              = "AzureActiveDirectory"
    unauthenticated_client_action = "RedirectToLoginPage"
              }

  identity {
                type = "SystemAssigned"
              }

  site_config {
    http2_enabled = true
  }
}

resource "azurerm_security_center_subscription_pricing" "example" {
      tier = "Standard"
    }

resource "azurerm_security_center_contact" "good-example" {
  email = "contact@example.com"
  phone = "+1-555-555-5555"

  alert_notifications = true
  alerts_to_admins    = true
}

resource "azurerm_sql_server" "example" {
  name                         = "mssqlserver"
  resource_group_name          = azurerm_resource_group.example.name
  location                     = azurerm_resource_group.example.location
  version                      = "12.0"
  administrator_login          = "mradministrator"
  administrator_login_password = "thisIsDog11"  # checkov:skip=CKV_SECRET_6 test secret

  extended_auditing_policy {
    storage_endpoint                        = azurerm_storage_account.example.primary_blob_endpoint
    storage_account_access_key              = azurerm_storage_account.example.primary_access_key
    storage_account_access_key_is_secondary = true
    retention_in_days                       = 100
  }
}

resource "azurerm_mssql_server_security_alert_policy" "example" {
  resource_group_name        = azurerm_resource_group.example.name
  server_name                = azurerm_sql_server.example.name
  state                      = "Enabled"
  storage_endpoint           = azurerm_storage_account.example.primary_blob_endpoint
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  disabled_alerts = []
  retention_days = 20
  email_addresses = ["example@gmail.com"]
  email_account_admins = true
}

resource "azurerm_mysql_server" "example" {
  name                = "example-mysqlserver"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name

  administrator_login          = "mysqladminun"
  administrator_login_password = "H@Sh1CoR3!"  # checkov:skip=CKV_SECRET_80 test secret

  sku_name   = "B_Gen5_2"
  storage_mb = 5120
  version    = "5.7"

  auto_grow_enabled                 = true
  backup_retention_days             = 7
  geo_redundant_backup_enabled      = true
  infrastructure_encryption_enabled = true
  public_network_access_enabled     = false
  ssl_enforcement_enabled           = true
  ssl_minimal_tls_version_enforced  = "TLS1_2"
}

resource "azurerm_postgresql_server" "example" {
  name                = "example-psqlserver"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  administrator_login          = "psqladminun"
  administrator_login_password = "H@Sh1CoR3!"
  sku_name   = "GP_Gen5_4"
  version    = "9.6"
  storage_mb = 640000
  backup_retention_days        = 7
  geo_redundant_backup_enabled = true
  auto_grow_enabled            = true
  public_network_access_enabled    = false
  ssl_enforcement_enabled          = true
  ssl_minimal_tls_version_enforced = "TLS1_2"
}

resource "azurerm_postgresql_configuration" "log-checkpoints-misconfig" {
  name                = "log_checkpoints"
  resource_group_name = data.azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.example.name
  value               = "off"
}

resource "azurerm_postgresql_configuration" "log-connections-misconfig" {
  name                = "log_connections"
  resource_group_name = data.azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.example.name
  value               = "off"
}

resource "azurerm_postgresql_configuration" "connection-throttling-misconfig" {
  name                = "connection-throttling"
  resource_group_name = data.azurerm_resource_group.example.name
  server_name         = azurerm_postgresql_server.example.name
  value               = "off"
}

resource "azurerm_storage_account" "example" {
  name                     = "arielkstorageaccount"
  resource_group_name      = data.azurerm_resource_group.example.name
  location                 = data.azurerm_resource_group.example.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  queue_properties  {

    logging {
      delete                = true
      read                  = true
      write                 = true
      version               = "1.0"
      retention_policy_days = 10
    }
    hour_metrics {
      enabled               = true
      include_apis          = true
      version               = "1.0"
      retention_policy_days = 10
    }
    minute_metrics {
      enabled               = true
      include_apis          = true
      version               = "1.0"
      retention_policy_days = 10
    }
  }
  network_rules {
    default_action             = "Deny"
    ip_rules                   = ["100.0.0.1"]
    virtual_network_subnet_ids = [azurerm_subnet.example.id]
  }
}

resource "azurerm_storage_account_network_rules" "test" {
  resource_group_name  = azurerm_resource_group.test.name
  storage_account_name = azurerm_storage_account.test.name

  default_action             = "Allow"
  ip_rules                   = ["127.0.0.1"]
  virtual_network_subnet_ids = [azurerm_subnet.test.id]
  bypass                     = ["Metrics"]
}

resource "azurerm_storage_container" "not-private-container" {
  name                  = "vhds"
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "blob"
}

resource "azurerm_monitor_log_profile" "example" {
  name = "default"

  categories = [
    "Action",
    "Delete",
    "Write",
  ]

  locations = [
    "westus",
    "global",
  ]

  # RootManageSharedAccessKey is created by default with listen, send, manage permissions
  servicebus_rule_id = "${azurerm_eventhub_namespace.example.id}/authorizationrules/RootManageSharedAccessKey"
  storage_account_id = azurerm_storage_account.example.id

  retention_policy {
    enabled = true
    days    = 365
  }
}

resource "azurerm_role_definition" "example" {
  name        = "my-custom-role"
  scope       = data.azurerm_subscription.primary.id
  description = "This is a custom role created via Terraform"

  permissions {
    actions     = ["*"]
    not_actions = []
  }

  assignable_scopes = [
    data.azurerm_subscription.primary.id
  ]
}

resource "azurerm_key_vault_key" "generated" {
  name         = "generated-certificate"
  key_vault_id = azurerm_key_vault.example.id
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
  expiration_date = "2020-12-30T20:00:00Z"
}

resource "azurerm_key_vault_secret" "example" {
  name         = "secret-sauce"
  value        = "szechuan"
  key_vault_id = azurerm_key_vault.example.id

  tags = {
    environment = "Production"
  }
  expiration_date = "2020-12-30T20:00:00Z"
}

resource "azurerm_key_vault" "example" {
  name                        = "testvault"
  location                    = azurerm_resource_group.example.location
  resource_group_name         = azurerm_resource_group.example.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_enabled         = true
  purge_protection_enabled    = true
  sku_name = "standard"
}

resource aws_s3_bucket "other-provider-bucket" {
  bucket   = "other_provider_bucket"
  provider = "non-default"
}

module "some-module" {
  source = "git::ssh://github.com/example/module//s3/s3-loggref=tags/1.0.0"
}


resource "google_sql_database_instance" "tfer--general-002D-mysql81" {
  database_version = "MYSQL_8_0"
  name             = "general-mysql81"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "true"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "false"
      start_time                     = "18:00"
    }

    crash_safe_replication = "false"

    database_flags {
      name  = "local_infile"
      value = "off"
    }

    disk_autoresize = "true"
    disk_size       = "10"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled = "true"
      require_ssl  = "false"
    }

    location_preference {
      zone = "us-central1-a"
    }

    maintenance_window {
      day  = "0"
      hour = "0"
    }

    pricing_plan     = "PER_USE"
    replication_type = "SYNCHRONOUS"
    tier             = "db-n1-standard-1"
  }
}

resource "google_sql_database_instance" "tfer--general-002D-pos121" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "false"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "true"
      start_time                     = "18:00"
    }

    crash_safe_replication = "false"

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_min_messages"
      value = "debug5"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    database_flags {
      name  = "log_temp_files"
      value = "0"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "-1"
    }

    disk_autoresize = "true"
    disk_size       = "10"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled = "true"
      require_ssl  = "false"
    }

    location_preference {
      zone = "us-central1-a"
    }

    maintenance_window {
      day  = "0"
      hour = "0"
    }

    pricing_plan     = "PER_USE"
    replication_type = "SYNCHRONOUS"
    tier             = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "tfer--general-002D-sqlserver12" {
  database_version = "SQLSERVER_2017_STANDARD"
  name             = "general-sqlserver12"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"

  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"

    backup_configuration {
      binary_log_enabled             = "false"
      enabled                        = "true"
      location                       = "us"
      point_in_time_recovery_enabled = "false"
      start_time                     = "00:00"
    }

    crash_safe_replication = "false"

    database_flags {
      name  = "cross db ownership chaining"
      value = "off"
    }

    database_flags {
      name  = "contained database authentication"
      value = "off"
    }

    disk_autoresize = "true"
    disk_size       = "20"
    disk_type       = "PD_SSD"

    ip_configuration {
      ipv4_enabled    = "false"
      private_network = "projects/gcp-bridgecrew-deployment/global/networks/default"
      require_ssl     = "false"
    }

    location_preference {
      zone = "us-central1-a"
    }

    maintenance_window {
      day  = "0"
      hour = "0"
    }

    pricing_plan     = "PER_USE"
    replication_type = "SYNCHRONOUS"
    tier             = "db-custom-1-4096"
  }
}
