# pass

resource "google_compute_firewall" "restricted" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["20"]
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ftp"]
}

resource "google_compute_firewall" "allow_different_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [4624]
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ftp"]
}

resource "google_compute_firewall" "allow_null" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = null
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ftp"]
}

# fail

resource "google_compute_firewall" "allow_all" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_ftp_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [20]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_multiple" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["1024-65535", "20"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# unknown

resource "google_compute_firewall" "allow_unknown" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow = "var.backends"

  source_ranges = ["0.0.0.0/0"]
}
