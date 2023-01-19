resource "google_compute_network" "fail" {
  name = "test-network"
  project = "pike-gcp"
}

resource "google_compute_firewall" "pass" {
  name    = "test-firewall"
  project = "pike-gcp"
  network = google_compute_network.pass.name
  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["80", "8080"]
  }

  source_tags = ["web"]
}

resource "google_compute_network" "pass" {
  name = "test-pass-network"
  project = "pike-gcp"
}
