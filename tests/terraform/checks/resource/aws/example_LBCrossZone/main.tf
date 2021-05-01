# pass

resource "aws_lb" "enabled" {
  internal           = false
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids

  enable_cross_zone_load_balancing = true
}

resource "aws_alb" "enabled" {
  load_balancer_type = "gateway"
  name               = "glb"

  enable_cross_zone_load_balancing = true

  subnet_mapping {
    subnet_id = var.subnet_id
  }
}

# failure

resource "aws_lb" "default" {
  internal           = false
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids
}

resource "aws_alb" "default" {
  load_balancer_type = "gateway"
  name               = "glb"

  subnet_mapping {
    subnet_id = var.subnet_id
  }
}

resource "aws_lb" "disabled" {
  internal           = false
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids

  enable_cross_zone_load_balancing = false
}

resource "aws_alb" "disabled" {
  load_balancer_type = "gateway"
  name               = "glb"

  enable_cross_zone_load_balancing = false

  subnet_mapping {
    subnet_id = var.subnet_id
  }
}

# unknown

resource "aws_lb" "application" {
  internal           = false
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
}

resource "aws_lb" "default_type" {
  internal           = false
  name               = "alb"
  subnets            = var.public_subnet_ids
}
