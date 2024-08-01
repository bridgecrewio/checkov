resource "aws_wafv2_web_acl" "pass_managed" {
  name          = var.name
  description   = "Managed by Terraform, do not edit in the console"
  scope         = "REGIONAL"
  token_domains = [var.dns.fqdn, aws_lb.this.dns_name]

  default_action {
    allow {}
  }

  rule {
    name     = "aws-managed-rules-common"
    priority = 1

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "friendly-rule-metric-name"
      sampled_requests_enabled   = false
    }
  }
  visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "friendly-rule-metric-name"
      sampled_requests_enabled   = false
  }
}

resource "aws_wafregional_web_acl" "pass" {
  name        = "example"
  metric_name = "example"

  default_action {
    type = "ALLOW"
  }

  rule {
    priority = 1
    rule_id  = aws_wafregional_rule_group.example.id
    type     = "GROUP"

    override_action {
      type = "NONE"
    }
  }
}

resource "aws_wafregional_web_acl" "pass2" {
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rule {
    action {
      type = "BLOCK"
    }

    priority = 1
    rule_id  = aws_wafregional_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_wafregional_web_acl" "fail" {
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rule {
    priority = 1
    rule_id  = aws_wafregional_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_wafregional_web_acl" "fail2" {
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rule {
    action {}

    priority = 1
    rule_id  = aws_wafregional_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_wafregional_web_acl" "pass3" {
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rule {
    action {
      type = "BLOCK"
    }

    priority = 1
    rule_id  = aws_wafregional_rule.wafrule.id
    type     = "REGULAR"
  }

    rule {
    action {
      type = "BLOCK"
    }

    priority = 2
    rule_id  = aws_wafregional_rule.wafrule2.id
    type     = "REGULAR"
  }
}

resource "aws_waf_web_acl" "pass" {
  depends_on = [
    aws_waf_ipset.ipset,
    aws_waf_rule.wafrule,
  ]
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rules {
    action {
      type = "BLOCK"
    }

    priority = 1
    rule_id  = aws_waf_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_waf_web_acl" "fail" {
  depends_on = [
    aws_waf_ipset.ipset,
    aws_waf_rule.wafrule,
  ]
  name        = "tfWebACL"
  metric_name = "tfWebACL"

  default_action {
    type = "ALLOW"
  }

  rules {
    priority = 1
    rule_id  = aws_waf_rule.wafrule.id
    type     = "REGULAR"
  }
}

resource "aws_wafv2_web_acl" "pass" {
  name        = "rate-based-example"
  description = "Example of a Cloudfront rate based statement."
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 10000
        aggregate_key_type = "IP"

        scope_down_statement {
          geo_match_statement {
            country_codes = ["US", "NL"]
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "friendly-rule-metric-name"
      sampled_requests_enabled   = false
    }
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_web_acl" "fail" {
  name        = "rate-based-example"
  description = "Example of a Cloudfront rate based statement."
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    statement {
      rate_based_statement {
        limit              = 10000
        aggregate_key_type = "IP"

        scope_down_statement {
          geo_match_statement {
            country_codes = ["US", "NL"]
          }
        }
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "friendly-rule-metric-name"
      sampled_requests_enabled   = false
    }
  }

  tags = {
    Tag1 = "Value1"
    Tag2 = "Value2"
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_rule_group" "pass" {
  name     = "example-rule"
  scope    = "REGIONAL"
  capacity = 2

  rule {
    name     = "rule-1"
    priority = 1

    action {
      allow {}
    }

    statement {

      geo_match_statement {
        country_codes = ["US", "NL"]
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = false
      metric_name                = "friendly-rule-metric-name"
      sampled_requests_enabled   = false
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafregional_rule_group" "pass" {
  name        = "example"
  metric_name = "example"

  activated_rule {
    action {
      type = "COUNT"
    }

    priority = 50
    rule_id  = aws_wafregional_rule.example.id
  }
}

resource "aws_waf_rule_group" "pass" {
  name        = "example"
  metric_name = "example"

  activated_rule {
    action {
      type = "COUNT"
    }

    priority = 50
    rule_id  = aws_waf_rule.example.id
  }
}

variable "scope" {
  type    = string # REGIONAL or CLOUDFRONT
  default = "CLOUDFRONT"
}


resource "aws_wafv2_web_acl" "pass_dynamic" {
  name  = "default-${var.scope}-web-acl"
  scope = var.scope


  default_action {
    block {}
  }


  rule {
    name     = "rule-${var.scope}-AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rule-${var.scope}-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rule-${var.scope}-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  dynamic "rule" {
    for_each = var.dynamic_ip_set == "" ? [] : [1]

    content {
      name     = "rule-${var.scope}-ip-allowlist"
      priority = 8

      action {
        allow {}
      }

      statement {
        or_statement {
          statement {
            ip_set_reference_statement {
              arn = aws_wafv2_ip_set.allow.arn
            }
          }
          statement {
            ip_set_reference_statement {
              arn = data.aws_wafv2_ip_set.github-actions[0].arn
            }
          }
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "rule-${var.scope}-ip-allowlist"
        sampled_requests_enabled   = true
      }
    }
  }


  dynamic "rule" {
    for_each = nonsensitive(var.review_token) == "" ? [] : [1]

    content {
      name     = "rule-${var.scope}-review-token-check"
      priority = 30

      action {
        allow {}
      }

      statement {
        byte_match_statement {
          positional_constraint = "EXACTLY"
          search_string         = var.review_token

          field_to_match {
            single_header {
              name = "review-token"
            }
          }

          text_transformation {
            priority = 1
            type     = "NONE"
          }
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "rule-${var.scope}-review-token-check"
        sampled_requests_enabled   = true
      }
    }
  }


  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.scope}-web-acl"
    sampled_requests_enabled   = true
  }
}