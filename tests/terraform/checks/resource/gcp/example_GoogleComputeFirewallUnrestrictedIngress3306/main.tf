#####################
## PASS TEST CASES ##
#####################

# Passes b/c we are specifying a restricted CIDR
resource "google_compute_firewall" "restricted" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["3306"]
  }

  source_ranges = ["172.1.2.3/32"]
}

# Passes b/c it does not match port 3306 +
# we are specifying a restricted CIDR
resource "google_compute_firewall" "allow_different_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [4624]
  }

  source_ranges = ["172.1.2.3/32"]
}

# Passes b/c the port is null and not 3306 +
# we are specifying a restricted CIDR
resource "google_compute_firewall" "allow_null" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = null
  }

  source_ranges = ["172.1.2.3/32"]
  target_tags   = ["mysql"]
}

#####################
## FAIL TEST CASES ##
#####################


# fails b/c of unrestricted CIDR +
# port 3306 is in the range
resource "google_compute_firewall" "allow_all" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# Fails b/c of unrestricted CIDR + port 3306
resource "google_compute_firewall" "allow_mysql_int" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = [3306]
  }

  source_ranges = ["0.0.0.0/0"]
}

# Fails b/c of unrestricted CIDR + port 3306
resource "google_compute_firewall" "allow_multiple" {
  name    = "example"
  network = "google_compute_network.vpc.name"

  allow {
    protocol = "tcp"
    ports    = ["4000-65535", "3306"]
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
