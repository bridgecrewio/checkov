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

resource "aws_apigatewayv2_domain_name" "example" {
  domain_name     = "api-v2.example.com"

  domain_name_configuration {
    certificate_arn = aws_acm_certificate_validation.example.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_route53_record" "pass_apiv2" {
  name    = aws_apigatewayv2_domain_name.example.domain_name
  type    = "A"
  zone_id = aws_route53_zone.example.id

  alias {
    evaluate_target_health = true
    name                   = aws_apigatewayv2_domain_name.example.target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.example.hosted_zone_id
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

resource "aws_route53_record" "ignore2" {
  # it is possible to have a plan with a route53 record that has no type. I am not sure how, but this is a test
  # of that case.
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "dns.freebeer.site"
  ttl     = "300"
  records = ["1.1.1.1"]
}

resource "aws_route53_record" "unknown" {
  zone_id = var.zone_id
  name = "test.example.com"
  type = "A"
  alias {
    name = module.alb.lb_dns_name
    zone_id = module.alb.lb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "unknown2" {
  zone_id = data.aws_route53_zone.example.zone_id
  name    = "example"
  type    = "A"

  alias {
    name                   = data.aws_lb.example.dns_name
    zone_id                = data.aws_lb.example.zone_id
    evaluate_target_health = true
  }
}

resource "aws_alb" "example" {
  name               = "example"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id]
}

resource "aws_route53_record" "pass_alb" {
  zone_id = data.aws_route53_zone.example.zone_id
  name    = "example"
  type    = "A"

  alias {
    name                   = aws_alb.example.dns_name
    zone_id                = aws_alb.example.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "pass5" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.fqdn
  type    = "A"
  alias {
    evaluate_target_health = false
    name                   = aws_cloudfront_distribution.website.domain_name
    zone_id                = aws_cloudfront_distribution.website.hosted_zone_id
  }
}

variable "aws_alb_dns_name" {}
variable "aws_alb_zone_id" {}

resource "aws_route53_record" "unknown3" {
  zone_id = data.aws_route53_zone.example.zone_id
  name    = "example"
  type    = "A"

  alias {
    name                   = var.aws_alb_dns_name
    zone_id                = var.aws_alb_zone_id
    evaluate_target_health = true
  }
}

resource "aws_cloudfront_distribution" "website" {
  provider = aws.useastone
  origin {
    domain_name = aws_s3_bucket.website.bucket_regional_domain_name
    origin_id   = "${aws_s3_bucket.website.id}-origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.website.cloudfront_access_identity_path
    }
  }
  web_acl_id = var.web_acl_id
  enabled         = true
  is_ipv6_enabled = true
  default_root_object = "index.html"
  custom_error_response {
    error_caching_min_ttl = 300
    error_code            = 404
    response_code         = 200
    response_page_path    = "/error.html"
  }
  aliases = [
    var.fqdn
  ]
  logging_config {
    bucket          = aws_s3_bucket.logging.bucket_domain_name
    include_cookies = false
    prefix          = "cloudfront/"
  }
  default_cache_behavior {
    allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods = [
      "GET",
      "HEAD",
    ]
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    min_ttl     = var.min_ttl
    default_ttl = var.default_ttl
    max_ttl     = var.max_ttl
    target_origin_id       = "${aws_s3_bucket.website.id}-origin"
    viewer_protocol_policy = "redirect-to-https"
  }
  ordered_cache_behavior {
    path_pattern     = "/content/immutable/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.s3_origin_id
    forwarded_values {
      query_string = false
      headers      = ["Origin"]
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
  # Cache behaviour with precedence 1
  ordered_cache_behavior {
    path_pattern     = "/content/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id
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
  price_class = var.price_class
  restrictions {
    geo_restriction {
      restriction_type = var.restriction_type
      locations = var.locations
    }
  }
  viewer_certificate {
    cloudfront_default_certificate = var.cloudfront_default_certificate
    acm_certificate_arn            = aws_acm_certificate.cert.arn
    ssl_support_method             = "sni-only"
    # tfsec:ignore:AWS021
    minimum_protocol_version = "TLSv1.2_2018"
  }
  retain_on_delete = var.retain
  tags             = var.common_tags
}

resource "aws_route53_record" "legacy-tf" {
  count = var.instance_count
  zone_id = data.aws_route53_zone.dns_zone.zone_id
  name = "brochureworker-${count.index + 1}.${data.aws_route53_zone.dns_zone.name}"
  type = "A"
  records = ["${aws_instance.brochureworker.*.private_ip[count.index]}"]
  ttl = "300"
}

resource "aws_instance" "brochureworker" {}

# ElasticBeanstalk

resource "aws_route53_record" "pass_eb" {
  zone_id = data.aws_route53_zone.dns_zone.zone_id
  name    = var.sub_domain
  type    = "A"

  alias {
    name                   =  aws_elastic_beanstalk_environment.pass_eb.cname
    zone_id                =  data.aws_elastic_beanstalk_hosted_zone.current.id
    evaluate_target_health = false
  }
}

resource "aws_elastic_beanstalk_environment" "pass_eb" {
  application = aws_elastic_beanstalk_application.example.name
  name        = "example"
}

# Lightsail

resource "aws_route53_record" "pass_lightsail" {
  zone_id  = data.aws_route53_zone.dns_zone.zone_id
  name     = var.sub_domain
  type     = "A"
  ttl      = "300"
  records  = [aws_lightsail_instance.example.public_ip_address]
}

resource "aws_lightsail_instance" "example" {
  name              = "example_lightsail_instance"
  availability_zone = "us-east-1f"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "medium_2_0"
}

resource "aws_route53_record" "pass_lightsail2" {
  zone_id = aws_route53_zone.primary.zone_id
  name = "mydomian.com"
  type = "A"
  ttl = "30"
  records = [aws_lightsail_static_ip.example.ip_address]
}

resource "aws_lightsail_static_ip" "example" {
  name = "pike"
}