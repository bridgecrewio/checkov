# pass

resource "google_compute_subnetwork" "pass" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.self_link"

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
  private_ip_google_access = true
}

# fail

resource "google_compute_subnetwork" "fail" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
}

resource "google_compute_subnetwork" "fail2" {
  name                     = "example"
  ip_cidr_range            = "10.0.0.0/16"
  network                  = "google_compute_network.vpc.id"
  private_ip_google_access = false
}