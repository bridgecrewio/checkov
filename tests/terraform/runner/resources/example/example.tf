provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
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
    admin_password = "Password1234!"
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
  #checkov:skip=CKV_AWS_52
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
}

resource "google_container_cluster" "primary_good2" {
  name               = "google_cluster"
  monitoring_service = "monitoring.googleapis.com"
}

resource "google_container_cluster" "primary_bad" {
  name               = "google_cluster_bad"
  monitoring_service = "none"
  enable_legacy_abac = true
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

resource "aws_iam_account_password_policy" "paswword-policy example with string values instead of int" {
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

resource "aws_security_group" "ingress as map instead of block" {
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
    #checkov:skip=CKV_AWS_52
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

resource "aws_s3_bucket" "dynamic ssee block as string" {
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

resource "aws_s3_bucket" "sse_block and rule_block as maps" {
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
      secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
  }
}

resource "aws_lambda_function" "block environment variables" {

  filename = "${path.module}/canary_sensor_api_capture.zip"
  description = "A lamba that reaches out to the Canary API used on the Canary website, obtains bearer tokens for communication, gets a list of the devices attached to the account, and fetches the sensor data for those devices."
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

resource "aws_lambda_function" "environment and variables with '= {' example" {
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

resource "aws_lambda_function" "dynamic environment that appears as string example" {
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
resource "aws_s3_bucket" "versioning as string example" {
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