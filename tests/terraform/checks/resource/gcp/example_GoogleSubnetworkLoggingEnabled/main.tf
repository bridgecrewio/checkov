# pass

resource "google_compute_subnetwork" "enabled" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.self_link"

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# fail

resource "google_compute_subnetwork" "default" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
}

# unknown

resource "google_compute_subnetwork" "internal_https_lb" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/22"
  network       = "google_compute_network.vpc.id"

  purpose = "INTERNAL_HTTPS_LOAD_BALANCER"
  role    = "ACTIVE"
}

resource "google_compute_subnetwork" "regional_managed_proxy" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/22"
  network       = "google_compute_network.vpc.id"

  purpose = "REGIONAL_MANAGED_PROXY"
  role    = "ACTIVE"
}

resource "google_compute_subnetwork" "global_managed_proxy" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/22"
  network       = "google_compute_network.vpc.id"

  purpose = "GLOBAL_MANAGED_PROXY"
  role    = "ACTIVE"
}