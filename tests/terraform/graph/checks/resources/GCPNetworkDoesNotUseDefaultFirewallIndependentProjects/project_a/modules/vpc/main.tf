variable "vpc_name" {
  type = string
}

resource "google_compute_network" "vpc" {
  name                    = var.vpc_name
  auto_create_subnetworks = false
}

output "network_name" {
  value = google_compute_network.vpc.name
}
