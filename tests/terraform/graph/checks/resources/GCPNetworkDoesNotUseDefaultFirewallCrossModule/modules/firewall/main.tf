resource "google_compute_firewall" "fw" {
  name    = var.fw_name
  network = var.network_name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["10.0.0.0/8"]
}
