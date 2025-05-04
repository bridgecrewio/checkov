resource "google_compute_network" "example" {
  name = "example"
  auto_create_subnetworks = false
}

#case1 - PASS - deny protocol
resource "google_compute_firewall" "compute-firewall-ok-1" {
  name    = "compute-firewall-ok-1"
  network = google_compute_network.example.name

  deny {
    protocol = "all"
  }
  source_ranges = ["0.0.0.0/0"]
  disabled = false
}

#case2 - PASS because disabled
resource "google_compute_firewall" "compute-firewall-ok-2" {
  name    = "compute-firewall-ok-2"
  network = google_compute_network.example.name

  allow {
    protocol = "all"
  }
  source_ranges = ["::/0"]
  disabled = true
}

#case3 - PASS
resource "google_compute_firewall" "compute-firewall-ok-3" {
  name    = "compute-firewall-ok-3"
  network = google_compute_network.example.name

  allow {
    protocol = "tcp"
    ports = ["140"]
  }
  source_ranges = ["0.0.0.0", "192.168.2.0"]
  disabled = false
}

#case4 - FAIL
resource "google_compute_firewall" "compute-firewall-not-ok-1" {
  name    = "compute-firewall-not-ok-1"
  network = google_compute_network.example.name

  allow {
    protocol = "all"
  }
  source_ranges = ["::/0"]
  disabled = false
}

#case5 - FAIL
resource "google_compute_firewall" "compute-firewall-not-ok-2" {
  name    = "compute-firewall-not-ok-2"
  network = google_compute_network.example.name

  allow {
    protocol = "all"
  }
  source_ranges = ["0.0.0.0", "192.168.2.0"]
  disabled = false
}

#case6 - FAIL
resource "google_compute_firewall" "compute-firewall-not-ok-3" {
  name    = "compute-firewall-not-ok-3"
  network = google_compute_network.example.name

  allow {
    protocol = "all"
  }
  source_ranges = ["0.0.0.0/0"]
  disabled = false
}

#case7 - FAIL
resource "google_compute_firewall" "compute-firewall-not-ok-4" {
  name    = "compute-firewall-not-ok-4"
  network = google_compute_network.example.name

  allow {
    protocol = "all"
  }
  source_ranges = ["::0"]
  disabled = false
}

# pass - source_ranges is ok
resource "google_compute_firewall" "pass_source_ranges" {
  name        = "pass_source_ranges"
  network     = "foo"
  project     = "foo"
  direction   = "INGRESS"
  disabled    = false
  description = "foo"
  priority    = 0
  allow {
    protocol = "all"
  }
  source_ranges = [
    "10.10.10.10/24",
    "10.11.10.10/24"
  ]
}

# fail - source_ranges is not ok
resource "google_compute_firewall" "fail_source_ranges" {
  name        = "pass_source_ranges"
  network     = "foo"
  project     = "foo"
  direction   = "INGRESS"
  disabled    = false
  description = "foo"
  priority    = 0
  allow {
    protocol = "all"
  }
  source_ranges = [
    "10.10.10.10/24",
    "10.11.10.10/24",
    "0.0.0.0/0"
  ]
}