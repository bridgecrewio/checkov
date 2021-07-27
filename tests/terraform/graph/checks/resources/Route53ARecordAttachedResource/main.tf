resource "aws_eip" "fixed" {
	# checkov:skip=CKV2_AWS_19: ADD REASON
}

resource "aws_route53_record" "pass" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "dns.freebeer.site"
  type    = "A"
  ttl     = "300"
  records = [aws_eip.fixed.public_ip]
}

resource "aws_api_gateway_domain_name" "example" {
  certificate_arn = aws_acm_certificate_validation.example.certificate_arn
  domain_name     = "api.example.com"
}

resource "aws_route53_record" "pass2" {
  name    = aws_api_gateway_domain_name.example.domain_name
  type    = "A"
  zone_id = aws_route53_zone.example.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.example.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.example.cloudfront_zone_id
  }
}



resource "aws_route53_record" "fail" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "dns.freebeer.site"
  type    = "A"
  ttl     = "300"
  records = ["1.1.1.1"]
}

resource "aws_route53_record" "ignore" {
  zone_id = data.aws_route53_zone.parent.id
  name    = "Some name abcd"
  type    = "CNAME"
  ttl     = 60
  records = [module.controller.loadbalancer_dns_name]
}

resource "aws_route53_record" "pass3" {
  zone_id = var.zone_id
  name = "test.example.com"
  type = "A"
  alias {
    name = module.alb.lb_dns_name
    zone_id = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "pass4" {
  zone_id = data.aws_route53_zone.example.zone_id
  name    = "example"
  type    = "A"

  alias {
    name                   = data.aws_lb.example.dns_name
    zone_id                = data.aws_lb.example.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "legacy-tf" {
  count = var.instance_count
  zone_id = data.aws_route53_zone.dns_zone.zone_id
  name = "brochureworker-${count.index + 1}.${data.aws_route53_zone.dns_zone.name}"
  type = "A"
  records = ["${aws_instance.brochureworker.*.private_ip[count.index]}"]
  ttl = "300"
}

resource "aws_instance" "brochureworker" {
}