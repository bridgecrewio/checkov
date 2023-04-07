# FAIL_1: All checks fail

resource "google_compute_firewall" "fail_1" {
  project     = "pud-fw-project"
  name        = "pud-fw-rule"
  network     = "default"
  description = "Creates firewall rule targeting tagged instances"
  direction   = INGRESS

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "udp"
  }

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "tcp"
    ports    = ["80", "27017", "22"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16", "0.0.0.0/0"]


  source_tags = ["foo"]
  target_tags = ["web"]
}

# FAIL_2: Simultaneously Protocol and source_ranges shoould not be equals to TCP/UDP and 0.0.0.0/0

resource "google_compute_firewall" "fail_2" {
  project     = "pud-fw-project"
  name        = "pud-fw-rule"
  network     = "default"
  description = "Creates firewall rule targeting tagged instances"
  direction   = INGRESS

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "udp"
  }

  allow {
    protocol = "tcp"
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16", "0.0.0.0/0"]


  source_tags = ["foo"]
  target_tags = ["web"]
}

# PASS: Even though the ports contains 23, source_ranges doesn't contain overly permissive IPs

resource "google_compute_firewall" "pass" {
  project     = "pud-fw-project"
  name        = "pud-fw-rule"
  network     = "default"
  description = "Creates firewall rule targeting tagged instances"
  direction   = INGRESS

  allow {
    protocol = "tcp"
    ports    = ["80", "27017", "22"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]


  source_tags = ["foo"]
  target_tags = ["web"]
}

