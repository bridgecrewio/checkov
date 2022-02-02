resource "aws_lb" "lb_good_1" {
  internal= false
}

resource "aws_lb" "lb_good_2" {
  internal= false
}

resource "aws_alb" "alb_good_1" {
  internal= false
}

resource "aws_wafregional_web_acl_association" "foo" {
  resource_arn = aws_lb.lb_good_1.arn
  web_acl_id = aws_wafregional_web_acl.foo.id
}

resource "aws_wafv2_web_acl_association" "bar" {
  resource_arn = aws_lb.lb_good_2.arn
  web_acl_arn = aws_wafv2_web_acl.bar.arn
}

resource "aws_wafv2_web_acl_association" "zed" {
  resource_arn = aws_alb.alb_good_1.arn
  web_acl_arn = aws_wafv2_web_acl.zed.arn
}

//public no WAF
resource "aws_lb" "lb_bad_1" {
  internal=false
}

//internal should ignore
resource "aws_lb" "ignore" {
  internal= true
}

//public internal not set (takes default - public)
resource "aws_lb" "lb_bad_2" {
}

//public no WAF
resource "aws_alb" "alb_bad_1" {
  internal=false
}

// NLB or Gateway LB can't have a WAF associated

resource "aws_lb" "network" {
  internal           = false
  load_balancer_type = "network"
  name               = "nlb"
  subnets            = var.public_subnet_ids
}

resource "aws_lb" "gateway" {
  load_balancer_type = "gateway"
  name               = "glb"

  subnet_mapping {
    subnet_id = var.subnet_id
  }
}
