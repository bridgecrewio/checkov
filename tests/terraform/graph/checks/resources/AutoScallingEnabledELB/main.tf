resource "aws_autoscaling_group" "autoscalling_ok" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true

  lifecycle {
    ignore_changes = [load_balancers, target_group_arns]
  }
}

resource "aws_autoscaling_attachment" "test_ok_attachment" {
  autoscaling_group_name = aws_autoscaling_group.autoscalling_ok.id
  elb                    = aws_elb.test_ok.id
}

resource "aws_elb" "test_ok" {
  name               = "foobar-terraform-elb"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  access_logs {
    bucket        = "foo"
    bucket_prefix = "bar"
    interval      = 60
  }

  listener {
    instance_port     = 8000
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  listener {
    instance_port      = 8000
    instance_protocol  = "http"
    lb_port            = 443
    lb_protocol        = "https"
    ssl_certificate_id = "arn:aws:iam::123456789012:server-certificate/certName"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:8000/"
    interval            = 30
  }

  instances                   = [aws_instance.foo.id]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags = {
    Name = "foobar-terraform-elb"
  }
}

resource "aws_autoscaling_group" "autoscalling_bad" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true

  lifecycle {
    ignore_changes = [load_balancers, target_group_arns]
  }
}

resource "aws_autoscaling_attachment" "test_bad_attachment" {
  autoscaling_group_name = aws_autoscaling_group.autoscalling_bad.id
  elb                    = aws_elb.test_bad.id
}

resource "aws_elb" "test_bad" {
  name               = "foobar-terraform-elb"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  access_logs {
    bucket        = "foo"
    bucket_prefix = "bar"
    interval      = 60
  }

  listener {
    instance_port     = 8000
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  listener {
    instance_port      = 8000
    instance_protocol  = "http"
    lb_port            = 443
    lb_protocol        = "https"
    ssl_certificate_id = "arn:aws:iam::123456789012:server-certificate/certName"
  }

  instances                   = [aws_instance.foo.id]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags = {
    Name = "foobar-terraform-elb"
  }
}

# LB
resource "aws_autoscaling_group" "alb_pass" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true

  lifecycle {
    ignore_changes = [load_balancers, target_group_arns]
  }
}

resource "aws_lb_target_group" "alb_pass" {
  name     = "tf-example-lb-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    port                = 8080
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    matcher             = "200-499"
  }
}

resource "aws_autoscaling_attachment" "alb_pass" {
  autoscaling_group_name = aws_autoscaling_group.alb_pass.id
  lb_target_group_arn    = aws_lb_target_group.alb_pass.arn
}

resource "aws_autoscaling_group" "alb_fail" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true

  lifecycle {
    ignore_changes = [load_balancers, target_group_arns]
  }
}

resource "aws_lb_target_group" "alb_fail" {
  name     = "tf-example-lb-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_autoscaling_attachment" "alb_fail" {
  autoscaling_group_name = aws_autoscaling_group.alb_fail.id
  lb_target_group_arn    = aws_lb_target_group.alb_fail.arn
}

# Inline load balancer association (no aws_autoscaling_attachment)
resource "aws_elb" "inline_elb" {
  name               = "foobar-terraform-elb-inline"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

  listener {
    instance_port     = 8000
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:8000/"
    interval            = 30
  }
}

resource "aws_autoscaling_group" "inline_elb" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  load_balancers            = [aws_elb.inline_elb.id]
}

resource "aws_autoscaling_group" "inline_ec2" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  desired_capacity          = 4
  force_delete              = true
  load_balancers            = [aws_elb.inline_elb.id]
}

# Inline target group association (no aws_autoscaling_attachment)
resource "aws_lb_target_group" "inline_tg" {
  name     = "tf-example-lb-tg-inline"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    port                = 8080
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    matcher             = "200-499"
  }
}

resource "aws_autoscaling_group" "inline_tg" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  target_group_arns         = [aws_lb_target_group.inline_tg.arn]
}

# No load balancer at all: out of scope, must not fail
resource "aws_autoscaling_group" "no_lb" {
  max_size                  = 5
  min_size                  = 2
  health_check_grace_period = 300
  desired_capacity          = 4
  force_delete              = true
}
