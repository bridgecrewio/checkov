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

resource "google_compute_forwarding_rule" "fail2" {
  name                  = "l7-ilb-forwarding-rule"
  provider              = google-beta
  region                = "europe-west1"
  depends_on            = [google_compute_subnetwork.proxy_subnet]
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_region_target_http_proxy.default.id
  network               = google_compute_network.ilb_network.id
  subnetwork            = google_compute_subnetwork.ilb_subnet.id
  network_tier          = "PREMIUM"
}

resource "google_compute_region_target_http_proxy" "default" {
  name     = "l7-ilb-target-http-proxy"
  provider = google-beta
  region   = "europe-west1"
  url_map  = google_compute_region_url_map.default.id
}