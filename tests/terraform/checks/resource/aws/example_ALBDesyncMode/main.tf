# pass

resource "aws_lb" "pass" {
  internal           = false
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
  desync_mitigation_mode = "strictest"
  drop_invalid_header_fields = true
}

resource "aws_alb" "pass" {
  internal           = false
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
  drop_invalid_header_fields = true
}

resource "aws_lb" "fail" {
  internal           = false
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
  desync_mitigation_mode = "monitor"
  drop_invalid_header_fields = true
}

resource "aws_alb" "fail" {
  internal           = false
  load_balancer_type = "application"
  name               = "alb"
  subnets            = var.public_subnet_ids
  drop_invalid_header_fields = true
  desync_mitigation_mode = "monitor"
}
