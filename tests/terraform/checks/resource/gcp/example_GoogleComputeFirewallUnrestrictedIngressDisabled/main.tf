resource "google_compute_firewall" "disabled_ssh_rdp" {
  name     = "example"
  network  = "google_compute_network.vpc.name"
  disabled = true

  allow {
    protocol = "tcp"
    ports    = ["22", "3389"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "disabled_false_ssh_rdp" {
  name     = "example"
  network  = "google_compute_network.vpc.name"
  disabled = false

  allow {
    protocol = "tcp"
    ports    = ["22", "3389"]
  }

  source_ranges = ["0.0.0.0/0"]
}

variable "firewall_disabled" {
  type = bool
}

resource "google_compute_firewall" "disabled_unresolved_ssh_rdp" {
  name     = "example"
  network  = "google_compute_network.vpc.name"
  disabled = var.firewall_disabled

  allow {
    protocol = "tcp"
    ports    = ["22", "3389"]
  }

  source_ranges = ["0.0.0.0/0"]
}
