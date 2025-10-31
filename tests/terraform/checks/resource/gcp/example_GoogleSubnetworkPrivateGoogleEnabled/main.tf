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

resource "google_compute_subnetwork" "pass2" {
  name          = "example"
  ip_cidr_range = "10.0.0.0/16"
  network       = "google_compute_network.vpc.self_link"
  purpose       = "PRIVATE_RFC_1918"
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

resource "google_compute_subnetwork" "unknown" {
  name    = "internal-https-lb-europe-west2"
  network = google_compute_network.pike.id
  region  = "europe-west2"

  ip_cidr_range = "10.0.0.0/24"
  purpose       = "INTERNAL_HTTPS_LOAD_BALANCER"
  role          = "ACTIVE"
}

resource "google_compute_subnetwork" "unknown2" {
  name    = "internal-https-lb-europe-west2"
  network = google_compute_network.pike.id
  region  = "europe-west2"

  ip_cidr_range = "10.0.0.0/24"
  purpose       = "REGIONAL_MANAGED_PROXY"
  role          = "ACTIVE"
}

resource "google_compute_subnetwork" "unknown3" {
  name    = "internal-https-lb-europe-west2"
  network = google_compute_network.pike.id
  region  = "europe-west2"

  ip_cidr_range = "10.0.0.0/24"
  purpose       = "GLOBAL_MANAGED_PROXY"
  role          = "ACTIVE"
}

 resource "google_compute_network" "pike" {
   auto_create_subnetworks = false
   name="pike"

 }


 provider "google" {
      project="pike-gcp"
 }