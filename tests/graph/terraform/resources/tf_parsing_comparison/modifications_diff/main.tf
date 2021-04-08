resource "google_compute_instance" "tfer--test3" {
  boot_disk {
    auto_delete = "true"
    device_name = "test3"
    mode        = "READ_WRITE"
    source      = "https://www.googleapis.com/compute/v1/projects/disco-sector-283918/zones/us-central1-a/disks/test3"
  }
  can_ip_forward      = "false"
  deletion_protection = "false"
  enable_display      = "false"
  machine_type        = "e2-medium"
  name                = "test3"
  network_interface {
    access_config {
      nat_ip       = "34.122.7.28"
      network_tier = "PREMIUM"
    }
    network            = "https://www.googleapis.com/compute/v1/projects/disco-sector-283918/global/networks/default"
    network_ip         = "10.128.0.4"
    subnetwork         = "https://www.googleapis.com/compute/v1/projects/disco-sector-283918/regions/us-central1/subnetworks/default"
    subnetwork_project = "disco-sector-283918"
  }
  project = "disco-sector-283918"
  scheduling {
    automatic_restart   = "true"
    on_host_maintenance = "MIGRATE"
    preemptible         = "false"
  }
  service_account {
    email  = "630155383092-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/devstorage.read_only", "https://www.googleapis.com/auth/trace.append", "https://www.googleapis.com/auth/servicecontrol", "https://www.googleapis.com/auth/service.management.readonly", "https://www.googleapis.com/auth/monitoring.write", "https://www.googleapis.com/auth/logging.write"]
  }
  shielded_instance_config {
    enable_integrity_monitoring = "true"
    enable_secure_boot          = "false"
    enable_vtpm                 = "true"
  }
  zone = "us-central1-a"
}