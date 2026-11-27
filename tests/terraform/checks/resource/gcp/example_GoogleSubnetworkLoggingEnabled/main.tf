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

resource "google_compute_subnetwork" "enabled_private" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = "PRIVATE"

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

resource "google_compute_subnetwork" "enabled_private_rfc_1918" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = "PRIVATE_RFC_1918"

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

resource "google_compute_subnetwork" "private_no_logs" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = "PRIVATE"
}

resource "google_compute_subnetwork" "null_purpose_no_logs" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = null
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

resource "google_compute_subnetwork" "private_service_connect" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = "PRIVATE_SERVICE_CONNECT"
}

resource "google_compute_subnetwork" "private_nat" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.id"
  purpose       = "PRIVATE_NAT"
}
