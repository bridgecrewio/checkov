resource "google_compute_forwarding_rule" "pass" {
  name                  = "passing-forwarding-rule"
  region                = "us-central1"
  load_balancing_scheme = "EXTERNAL"
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetHttpProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_forwarding_rule" "fail" {
  name                  = "failing-forwarding-rule"
  region                = "us-central1"
  load_balancing_scheme = "EXTERNAL"
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetSslProxies/my-target-proxy"

  // Additional required configuration as needed...
}

resource "google_compute_forwarding_rule" "fail_missing_lbscheme" {
  name                  = "failing-forwarding-rule"
  region                = "us-central1"
  # load_balancing_scheme = "EXTERNAL" # Default is EXTERNAL
  target                = "https://www.googleapis.com/compute/v1/projects/my-project/global/targetSslProxies/my-target-proxy"

  // Additional required configuration as needed...
}
