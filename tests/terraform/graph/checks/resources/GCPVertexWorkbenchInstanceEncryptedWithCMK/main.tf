resource "google_workbench_instance" "instance_bad" {
  name = "workbench-instance-bad"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = false

    service_accounts {
      email = "my@service-account.com"
    }

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
    }

    data_disks {
      disk_size_gb  = 330
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
    }

    network_interfaces {
      network = google_compute_network.my_network.id
      subnet = google_compute_subnetwork.my_subnetwork.id
      nic_type = "GVNIC"
    }

    metadata = {
      terraform = "true"
    }

    enable_ip_forwarding = true
  }
}

resource "google_workbench_instance" "instance_bad_nodata" {
  name = "workbench-instance-bad"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = false

    service_accounts {
      email = "my@service-account.com"
    }

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
    }

    data_disks {
      disk_size_gb  = 330
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
    }

    network_interfaces {
      network = google_compute_network.my_network.id
      subnet = google_compute_subnetwork.my_subnetwork.id
      nic_type = "GVNIC"
    }

    metadata = {
      terraform = "true"
    }

    enable_ip_forwarding = true
  }
}

resource "google_workbench_instance" "instance_bad_nogcesetup" {
  name = "workbench-instance-bad"
  location = "us-central1-a"
}

resource "google_workbench_instance" "instance_good" {
  name = "workbench-instance-good"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = false

    service_accounts {
      email = "my@service-account.com"
    }

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "CMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }

    data_disks {
      disk_size_gb  = 330
      disk_type = "PD_SSD"
      disk_encryption = "CMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }

    network_interfaces {
      network = google_compute_network.my_network.id
      subnet = google_compute_subnetwork.my_subnetwork.id
      nic_type = "GVNIC"
    }

    metadata = {
      terraform = "true"
    }

    enable_ip_forwarding = true
  }
}

resource "google_workbench_instance" "instance_good_nodata" {
  name = "workbench-instance-good"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = false

    service_accounts {
      email = "my@service-account.com"
    }

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "CMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }

    network_interfaces {
      network = google_compute_network.my_network.id
      subnet = google_compute_subnetwork.my_subnetwork.id
      nic_type = "GVNIC"
    }

    metadata = {
      terraform = "true"
    }

    enable_ip_forwarding = true
  }
}