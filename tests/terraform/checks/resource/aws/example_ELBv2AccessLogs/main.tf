# pass

resource "aws_lb" "enabled" {
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket  = var.bucket_name
    enabled = true
  }
}

resource "aws_alb" "enabled" {
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket  = var.bucket_name
    enabled = true
  }
}

# failure

resource "aws_lb" "default" {
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids
}

resource "aws_alb" "default" {
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
}

resource "aws_lb" "only_bucket" {
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket = var.bucket_name
  }
}

resource "aws_alb" "only_bucket" {
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket = var.bucket_name
  }
}

resource "aws_lb" "disabled" {
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket  = var.bucket_name
    enabled = false
  }
}

resource "aws_alb" "disabled" {
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids

  access_logs {
    bucket  = var.bucket_name
    enabled = false
  }
}

# unknown

resource "aws_lb" "gateway" {
  name = "glb"
  load_balancer_type = "gateway"

  subnet_mapping {
    subnet_id = var.subnet_id
  }
}

