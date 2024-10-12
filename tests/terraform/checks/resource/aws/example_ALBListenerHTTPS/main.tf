resource "aws_lb_target_group" "example" {
  name     = "example-tg"
}

resource "aws_lb" "example" {
  name               = "example-lb"
}

resource "aws_lb_listener" "fail" {
  for_each = { for idx, lr in var.listener_rules : tostring(idx) => lr }
  load_balancer_arn = aws_lb.example.arn
  port              = try(each.value.port, var.default_port)
  protocol          = try(each.value.protocol, var.default_protocol)

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.example.arn
  }
}

resource "aws_lb_listener" "pass" {
  for_each = { for idx, lr in var.listener_rules : tostring(idx) => lr }
  load_balancer_arn = aws_lb.example.arn
  port              = try(each.value.port, var.default_port)
  protocol          = try(each.value.protocol, var.default_protocol)

  default_action {
    type             = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

variable "listener_rules" {
  default = [{
    "port": "0",
    "protocol": "HTTPS",
  },
  {
    "port": "80",
    "protocol": "HTTPS",
  }]
}

variable "default_protocol" {
  description = "Default protocol used across the listener and target group"
  type        = string
  default     = "HTTP"
}

variable "default_port" {
  type        = string
  default     = "80"
}