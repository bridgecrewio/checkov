resource "aws_lb_listener" "pass" {
  load_balancer_arn = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188"
  port              = 443
  protocol          = "TLS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "arn:aws:iam::123456789012:server-certificate/test_cert"

  mutual_authentication {
    mode            = "verify"
    trust_store_arn = "arn:aws:elasticloadbalancing:us-east-1:123456789012:truststore/my-trust-store/50dc6c495c0c9188"
  }
}
