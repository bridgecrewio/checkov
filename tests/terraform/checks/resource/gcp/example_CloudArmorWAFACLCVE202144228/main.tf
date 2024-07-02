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