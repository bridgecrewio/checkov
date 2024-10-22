# pass

resource "google_compute_firewall" "restricted" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ssh"]
}

resource "google_compute_firewall" "allow_different_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [4624]
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ssh"]
}

resource "google_compute_firewall" "allow_null" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = null
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["ssh"]
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

resource "google_compute_firewall" "allow_ssh_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [22]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_multiple" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["1024-65535", "22"]
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

# foreach example

locals {
firewall = {
  "firewall-01" = { name = "name-open-ssh", tag = ["allow-ssh"], port = ["22"], range = ["0.0.0.0/0"] },
  "firewall-02" = { name = "name-open-rdp", tag = ["allow-rdp"], port = ["3389"], range = ["0.0.0.0/0"] },
  "firewall-04" = { name = "name-open-telnet", tag = ["allow-telnet"], port = ["23"], range = ["0.0.0.0/0"] },
  "firewall-05" = { name = "name-open-ciscosecure", tag = ["allow-ciscosecure"], port = ["9090"], range = ["0.0.0.0/0"] },
  "firewall-06" = { name = "name-open-opendir", tag = ["allow-opendir"], port = ["445"], range = ["0.0.0.0/0"] },
  }
}

resource "google_compute_firewall" "firewall_demo" {
  for_each = local.firewall
  name = each.value.name
  network = "google_compute_network.vpc_network.id"
  project = "var.project_id"
  target_tags = each.value.tag

  allow {
    protocol = "tcp"
    ports = each.value.port
  }
  source_ranges = each.value.range
}