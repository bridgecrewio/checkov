# pass

resource "google_container_cluster" "restricted" {
  name     = "restricted-cluster"
  location = "us-central1"

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.0.0.0/8"
      display_name = "internal"
    }
  }
}

resource "google_container_cluster" "private_endpoint" {
  name     = "private-cluster"
  location = "us-central1"

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = true
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
}

# fail

resource "google_container_cluster" "open" {
  name     = "open-cluster"
  location = "us-central1"

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "the world"
    }
  }
}

resource "google_container_cluster" "no_man_config" {
  name     = "no-man-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1
}
