resource "google_workbench_instance" "instance_explicitly_bad" {
  name = "workbench-instance-bad"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = false

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }
  }
}

resource "google_workbench_instance" "instance_bad" {
  name = "workbench-instance-bad"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }
  }
}

resource "google_workbench_instance" "instance_bad_nogcesetup" {
  name = "workbench-instance-bad-nogcesetup"
  location = "us-central1-a"
}

resource "google_workbench_instance" "instance_good" {
  name = "workbench-instance-bad"
  location = "us-central1-a"

  gce_setup {
    machine_type = "n1-standard-4"
    accelerator_configs {
      type         = "NVIDIA_TESLA_T4"
      core_count   = 1
    }

    disable_public_ip = true

    boot_disk {
      disk_size_gb  = 310
      disk_type = "PD_SSD"
      disk_encryption = "GMEK"
      kms_key = google_kms_crypto_key.crypto-key.id
    }
  }
}