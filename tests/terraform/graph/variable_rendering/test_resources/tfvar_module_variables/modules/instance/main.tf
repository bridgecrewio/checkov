resource "google_compute_instance" "instance" {
  name         = var.var_instance.instance_name
  machine_type = var.var_instance.instance_machine_type
  zone         = var.var_instance.instance_zone

  tags = ["foofoo", "barbar"]

  boot_disk {
    initialize_params {
      image = var.var_instance.instance_image
    }
  }

  // Local SSD disk
  scratch_disk {
    interface = var.var_instance.instance_interface_disk
  }

  network_interface {
    network = var.var_instance.instance_network

    access_config {
      // Ephemeral IP
    }
  }

  metadata = {
    env = var.var_instance.meta_env
  }

  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
  }
}
