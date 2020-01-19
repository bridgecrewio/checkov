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

resource "aws_iam_account_password_policy" "password-policy" {
  minimum_password_length        = 15
  require_lowercase_characters   = true
  require_numbers                = true
  require_uppercase_characters   = true
  require_symbols                = true
  allow_users_to_change_password = true
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