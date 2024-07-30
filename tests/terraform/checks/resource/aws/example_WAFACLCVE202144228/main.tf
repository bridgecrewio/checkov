# pass

resource "aws_wafv2_web_acl" "pass" {
  name        = "managed-rule-example"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"

        excluded_rule {
          name = "Host_localhost_HEADER"
        }
        excluded_rule {
          name = "PROPFIND_METHOD"
        }
        excluded_rule {
          name = "ExploitablePaths_URIPATH"
        }
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

resource "aws_wafv2_web_acl" "multi_rules" {
  name        = "managed-rule-example"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "aws-managed-known-bad-inputs"
    priority = 1
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
      metric_name                = "aws-managed-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws-managed-common-rule-set"
    priority = 2
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
        excluded_rule {
          name = "SizeRestrictions_BODY"
        }
        excluded_rule {
          name = "CrossSiteScripting_COOKIE"
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "aws-managed-common-rule-set"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "rate-limit-ip"
    priority = 3

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rate-limit-ip"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

# fail

resource "aws_wafv2_web_acl" "no_rule" {
  name        = "managed-rule-example-fail"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = false
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_web_acl" "wrong_rule" {
  name        = "managed-rule-example"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesAnonymousIpList"
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
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}

resource "aws_wafv2_web_acl" "rule_count" {
  name        = "managed-rule-example"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"

        excluded_rule {
          name = "Log4JRCE"
        }
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

resource "aws_wafv2_web_acl" "rule_group_count" {
  name        = "managed-rule-example"
  description = "Example of a managed rule."
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "rule-1"
    priority = 1

    override_action {
      count {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
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
    metric_name                = "friendly-metric-name"
    sampled_requests_enabled   = false
  }
}


#unknown
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
