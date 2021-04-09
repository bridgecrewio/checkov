
resource "google_container_cluster" "fail1" {
  name               = var.name
  location           = var.location
  initial_node_count = 1
  project            = data.google_project.project.name

  network    = var.network
  subnetwork = var.subnetwork

  ip_allocation_policy {
    cluster_ipv4_cidr_block       = var.ip_allocation_policy["cluster_ipv4_cidr_block"]
    cluster_secondary_range_name  = var.ip_allocation_policy["cluster_secondary_range_name"]
    services_ipv4_cidr_block      = var.ip_allocation_policy["services_ipv4_cidr_block"]
    services_secondary_range_name = var.ip_allocation_policy["services_secondary_range_name"]
  }

  remove_default_node_pool = var.remove_default_node_pool

  node_config {
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
  }

  release_channel {
    channel = var.release_channel
  }

  master_auth {

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  addons_config {
    http_load_balancing {
      disabled = var.http_load_balancing_disabled
    }

    network_policy_config {
      disabled = var.network_policy_config_disabled
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_window
    }
  }

  private_cluster_config {
    enable_private_nodes    = var.private_cluster_config["enable_private_nodes"]
    enable_private_endpoint = var.private_cluster_config["enable_private_endpoint"]
    master_ipv4_cidr_block  = var.private_cluster_config["master_ipv4_cidr_block"]
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block = var.master_authorized_network_cidr
    }
  }

  network_policy {
    enabled = true
  }

  pod_security_policy_config {
    enabled = var.pod_security_policy_config_enabled
  }

  resource_labels = var.resource_labels
}

resource "google_container_cluster" "fail2" {
  name               = var.name
  location           = var.location
  initial_node_count = 1
  project            = data.google_project.project.name

  network    = var.network
  subnetwork = var.subnetwork

  ip_allocation_policy {
    cluster_ipv4_cidr_block       = var.ip_allocation_policy["cluster_ipv4_cidr_block"]
    cluster_secondary_range_name  = var.ip_allocation_policy["cluster_secondary_range_name"]
    services_ipv4_cidr_block      = var.ip_allocation_policy["services_ipv4_cidr_block"]
    services_secondary_range_name = var.ip_allocation_policy["services_secondary_range_name"]
  }

  remove_default_node_pool = var.remove_default_node_pool

  enable_shielded_nodes = false

  node_config {
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
    shielded_instance_config {
      enable_secure_boot = false
    }
  }

  release_channel {
    channel = var.release_channel
  }

  master_auth {

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  addons_config {
    http_load_balancing {
      disabled = var.http_load_balancing_disabled
    }

    network_policy_config {
      disabled = var.network_policy_config_disabled
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_window
    }
  }

  private_cluster_config {
    enable_private_nodes    = var.private_cluster_config["enable_private_nodes"]
    enable_private_endpoint = var.private_cluster_config["enable_private_endpoint"]
    master_ipv4_cidr_block  = var.private_cluster_config["master_ipv4_cidr_block"]
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block = var.master_authorized_network_cidr
    }
  }

  network_policy {
    enabled = true
  }

  pod_security_policy_config {
    enabled = var.pod_security_policy_config_enabled
  }

  resource_labels = var.resource_labels
}

resource "google_container_node_pool" "fail1" {
  project  = data.google_project.project.name
  name     = var.node_pool["name"]
  location = var.location
  cluster  = google_container_cluster.cluster.name

  node_count        = var.node_pool["node_count"]
  max_pods_per_node = var.node_pool["max_pods_per_node"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }
}

resource "google_container_node_pool" "fail2" {
  project  = data.google_project.project.name
  name     = var.node_pool["name"]
  location = var.location
  cluster  = google_container_cluster.cluster.name

  node_count        = var.node_pool["node_count"]
  max_pods_per_node = var.node_pool["max_pods_per_node"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
    shielded_instance_config {
      enable_secure_boot = false
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }
}

resource "google_container_node_pool" "success" {
  project  = data.google_project.project.name
  name     = var.node_pool["name"]
  location = var.location
  cluster  = google_container_cluster.cluster.name

  node_count        = var.node_pool["node_count"]
  max_pods_per_node = var.node_pool["max_pods_per_node"]

  node_config {
    machine_type = var.node_pool["machine_type"]
    disk_size_gb = var.node_pool["disk_size_gb"]
    disk_type    = var.node_pool["disk_type"]

    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }

    shielded_instance_config {
      enable_secure_boot = true
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/compute",
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }
}

resource "google_container_cluster" "success" {
  name               = var.name
  location           = var.location
  initial_node_count = 1
  project            = data.google_project.project.name

  network    = var.network
  subnetwork = var.subnetwork

  ip_allocation_policy {
    cluster_ipv4_cidr_block       = var.ip_allocation_policy["cluster_ipv4_cidr_block"]
    cluster_secondary_range_name  = var.ip_allocation_policy["cluster_secondary_range_name"]
    services_ipv4_cidr_block      = var.ip_allocation_policy["services_ipv4_cidr_block"]
    services_secondary_range_name = var.ip_allocation_policy["services_secondary_range_name"]
  }

  remove_default_node_pool = var.remove_default_node_pool

  min_master_version = "1.12"

  node_config {
    workload_metadata_config {
      node_metadata = "GKE_METADATA_SERVER"
    }
    shielded_instance_config {
      enable_integrity_monitoring = true
      enable_secure_boot = true
    }
  }

  release_channel {
    channel = var.release_channel
  }

  master_auth {

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  addons_config {
    http_load_balancing {
      disabled = var.http_load_balancing_disabled
    }

    network_policy_config {
      disabled = var.network_policy_config_disabled
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = var.maintenance_window
    }
  }

  private_cluster_config {
    enable_private_nodes    = var.private_cluster_config["enable_private_nodes"]
    enable_private_endpoint = var.private_cluster_config["enable_private_endpoint"]
    master_ipv4_cidr_block  = var.private_cluster_config["master_ipv4_cidr_block"]
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block = var.master_authorized_network_cidr
    }
  }

  network_policy {
    enabled = true
  }

  pod_security_policy_config {
    enabled = var.pod_security_policy_config_enabled
  }

  resource_labels = var.resource_labels
}


