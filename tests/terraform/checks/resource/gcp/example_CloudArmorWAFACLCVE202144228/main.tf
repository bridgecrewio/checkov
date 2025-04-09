# pass

resource "google_compute_security_policy" "enabled_deny_403" {
  name = "example"

  rule {
    action   = "deny(403)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('cve-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "enabled_deny_404" {
  name = "example"

  rule {
    action   = "deny(404)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('cve-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "pass_preconfigwaf" {
  name = "example"

  rule {
    action   = "deny(403)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('cve-canary')"
        # expression = "evaluatePreconfiguredExpr('cve-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "pass_separate_resource" {
  name        = "example_separate"

  rule {
    description = "Foo"
    priority    = 1

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    action = "deny(404)"
  }
}

resource "google_compute_security_policy_rule" "cve_canary_waf" {
  security_policy = google_compute_security_policy.pass_separate_resource.name
  description = "cve-canary WAF rule"
  priority    = 1
  match {
    expr {
      expression = "evaluatePreconfiguredExpr('cve-canary')"
    }
  }
  action          = "deny(403)"
}

resource "google_compute_security_policy_rule" "rule2" {
  security_policy = google_compute_security_policy.pass_separate_resource.name
  description = "rule2"
  priority    = 2
  match {
    expr {
      expression = "evaluatePreconfiguredWaf('xss-canary')"
    }
  }
  action          = "allow"
}


# fail

resource "google_compute_security_policy" "allow" {
  name = "example"

  rule {
    action   = "allow"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('cve-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "preview" {
  name = "example"

  rule {
    action   = "deny(403)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('cve-canary')"
      }
    }
    preview = true
  }
}

resource "google_compute_security_policy" "different_expr" {
  name = "example"

  rule {
    action   = "deny(403)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "pass_preconfigwaf" {
  name = "example"

  rule {
    action   = "deny(403)"
    priority = 1
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('xss-canary')"
        # expression = "evaluatePreconfiguredExpr('xss-canary')"
      }
    }
  }
}

resource "google_compute_security_policy" "fail" {

  name = "my-policy"

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["9.9.9.0/24"]
      }
    }
    description = "Deny access to IPs in 9.9.9.0/24"
  }

  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "default rule"
  }
}

resource "google_compute_security_policy" "fail_separate_resource" {
  name        = "example_separate_fail"

  rule {
    description = "Foo"
    priority    = 1

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    action = "deny(404)"
  }
}

resource "google_compute_security_policy_rule" "cve_canary_waf" {
  security_policy = google_compute_security_policy.fail_separate_resource.name
  description = "cve-canary WAF rule"
  priority    = 1
  match {
    expr {
      expression = "evaluatePreconfiguredExpr('cve-canary')"
    }
  }
  action          = "allow"
}

resource "google_compute_security_policy_rule" "rule2" {
  security_policy = google_compute_security_policy.fail_separate_resource.name
  description = "rule2"
  priority    = 2
  match {
    expr {
      expression = "evaluatePreconfiguredWaf('xss-canary')"
    }
  }
  action          = "allow"
}