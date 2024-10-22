# this file is meant to be run with the following checks enabled: CKV_AWS_21, CKV_AWS_18, CKV_AWS_79, CKV_AWS_19
# (or anything else with no hardcoded suppressions)

resource "aws_s3_bucket" "financials" {
  # expected platform suppressions: CKV_AWS_21 (Resource), CKV_AWS_18 (Account)
  bucket        = "${local.resource_prefix.value}-financials"
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket" "operations" {
  # expected platform suppressions: CKV_AWS_21 (Tags), CKV_AWS_18 (Account)
  bucket        = "${local.resource_prefix.value}-operations"
  acl           = "private"
  force_destroy = true
  tags          = {
    Name        = "${local.resource_prefix.value}-operations"
    Environment = "418408045322-acme-dev"
  }
}

resource "aws_s3_bucket" "hello" {
  # expected platform suppressions: CKV_AWS_18 (Account)
  bucket        = "${local.resource_prefix.value}-data"
  acl           = "public-read"
  force_destroy = true
  tags = {
    Name        = "${local.resource_prefix.value}-data"
    Environment = local.resource_prefix.value
  }
}

resource "aws_instance" "web_host" {
  # expected platform suppressions: CKV_AWS_79 (Policy)
  ami           = "${var.ami}"
  instance_type = "t2.nano"

  vpc_security_group_ids = [
    "${aws_security_group.web-node.id}"]
  subnet_id              = "${aws_subnet.web_subnet.id}"
  user_data              = <<EOF
#! /bin/bash
sudo apt-get update
sudo apt-get install -y apache2
sudo systemctl start apache2
sudo systemctl enable apache2
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMAAA  # checkov:skip=CKV_SECRET_2 test secret
export AWS_SECRET_ACCESS_KEY=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  # checkov:skip=CKV_SECRET_6 test secret
export AWS_DEFAULT_REGION=us-west-2
echo "<h1>Deployed via Terraform</h1>" | sudo tee /var/www/html/index.html
EOF
  tags                   = {
    Name = "${local.resource_prefix.value}-ec2"
  }
}
