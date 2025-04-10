resource "google_compute_subnetwork" "fail" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  # purpose="INTERNAL_HTTPS_LOAD_BALANCER" if set ignored
  # log_config {
  #   metadata="EXCLUDE_ALL_METADATA"
  # }
  private_ip_google_access   = false
  private_ipv6_google_access = false
}

resource "google_compute_subnetwork" "fail2" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  # purpose="INTERNAL_HTTPS_LOAD_BALANCER" if set ignored
  # log_config {
  #   metadata="EXCLUDE_ALL_METADATA"
  # }
  private_ip_google_access = false
}

resource "google_compute_subnetwork" "unknown" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_ONLY"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  # purpose="INTERNAL_HTTPS_LOAD_BALANCER" if set ignored
  # log_config {
  #   metadata="EXCLUDE_ALL_METADATA"
  # }
  private_ip_google_access = false
}

resource "google_compute_subnetwork" "pass_out" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  # purpose="INTERNAL_HTTPS_LOAD_BALANCER" if set ignored
  # log_config {
  #   metadata="EXCLUDE_ALL_METADATA"
  # }
  private_ip_google_access   = true
  private_ipv6_google_access = "ENABLE_OUTBOUND_VM_ACCESS_TO_GOOGLE"
}

resource "google_compute_subnetwork" "pass_bidi" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  # purpose="INTERNAL_HTTPS_LOAD_BALANCER" if set ignored
  # log_config {
  #   metadata="EXCLUDE_ALL_METADATA"
  # }
  private_ip_google_access   = true
  private_ipv6_google_access = "ENABLE_BIDIRECTIONAL_ACCESS_TO_GOOGLE"
}


resource "google_compute_subnetwork" "unknown2" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
   purpose="INTERNAL_HTTPS_LOAD_BALANCER"
   log_config {
     metadata="EXCLUDE_ALL_METADATA"
   }
}

resource "google_compute_subnetwork" "unknown3" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  # No stack_type defaults to IPV4_ONLY
  # stack_type       = "IPV4_IPV6"
  ipv6_access_type = "EXTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
   purpose="INTERNAL_HTTPS_LOAD_BALANCER"
   log_config {
     metadata="EXCLUDE_ALL_METADATA"
   }
}

resource "google_compute_subnetwork" "unknown4" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "INTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  purpose          = "REGIONAL_MANAGED_PROXY"
  role             = "ACTIVE"

}

resource "google_compute_subnetwork" "unknown5" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "INTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  purpose          = "GLOBAL_MANAGED_PROXY"
  role             = "ACTIVE"
}

resource "google_compute_subnetwork" "unknown6" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "INTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  purpose          = "REGIONAL_MANAGED_PROXY"
  role             = "ACTIVE"
}

resource "google_compute_subnetwork" "unknown7" {
  name             = "log-test-subnetwork"
  ip_cidr_range    = "10.2.0.0/16"
  stack_type       = "IPV4_IPV6"
  ipv6_access_type = "INTERNAL"
  region           = "us-central1"
  network          = google_compute_network.custom-test.id
  purpose          = "GLOBAL_MANAGED_PROXY"
}