resource "google_compute_global_forwarding_rule" "fail" {
  name                  = "passing-forwarding-rule"
  load_balancing_scheme = "EXTERNAL"
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetHttpProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_global_forwarding_rule" "pass_not_external" {
  name                  = "passing-forwarding-rule"
  load_balancing_scheme = "INTERNAL_SELF_MANAGED"
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetHttpProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_global_forwarding_rule" "pass_nothttp" {
  name                  = "failing-forwarding-rule"
  load_balancing_scheme = "EXTERNAL"
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetSslProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_global_forwarding_rule" "fail_missing_lbscheme" {
  name                  = "failing-forwarding-rule"
  # load_balancing_scheme = "EXTERNAL" # Default is EXTERNAL
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetHttpProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_global_forwarding_rule" "default" {
  name                  = "l7-xlb-forwarding-rule"
  provider              = google-beta
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}

# http proxy
resource "google_compute_target_http_proxy" "default" {
  name     = "l7-xlb-target-http-proxy"
  provider = google-beta
  url_map  = google_compute_url_map.default.id
}
