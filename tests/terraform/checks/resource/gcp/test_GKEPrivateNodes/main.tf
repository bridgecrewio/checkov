
resource "google_container_cluster" "fail" {
  name               = var.name
  location           = var.location
  initial_node_count = 1
  project            = data.google_project.project.name

  network    = var.network
  subnetwork = var.subnetwork
}


resource "google_container_cluster" "success" {
  name               = var.name
  location           = var.location
  initial_node_count = 1
  project            = data.google_project.project.name

  network    = var.network
  subnetwork = var.subnetwork

  private_cluster_config {
    enable_private_nodes    = var.private_cluster_config["enable_private_nodes"]
    enable_private_endpoint = var.private_cluster_config["enable_private_endpoint"]
    master_ipv4_cidr_block  = var.private_cluster_config["master_ipv4_cidr_block"]
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block       = var.ip_allocation_policy["cluster_ipv4_cidr_block"]
    cluster_secondary_range_name  = var.ip_allocation_policy["cluster_secondary_range_name"]
    services_ipv4_cidr_block      = var.ip_allocation_policy["services_ipv4_cidr_block"]
    services_secondary_range_name = var.ip_allocation_policy["services_secondary_range_name"]
  }

  node_config {
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }

  release_channel {
    channel = var.release_channel
  }

}
