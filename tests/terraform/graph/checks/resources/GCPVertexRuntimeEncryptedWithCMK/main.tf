resource "google_notebooks_runtime" "runtime_good" {
  name = "notebooks-runtime-good"
  location = "us-central1"
  access_config {
    access_type = "SINGLE_USER"
    runtime_owner = "example@paloaltonetworks.com"
  }
  virtual_machine {
    virtual_machine_config {
      encryption_config {
        kms_key = "an-actual-key"
      }
      machine_type = "n1-standard-4"
      data_disk {
        initialize_params {
          disk_size_gb = "100"
          disk_type = "PD_STANDARD"
        }
      }
    }
  }
}

resource "google_notebooks_runtime" "runtime_bad_unset" {
  name = "notebooks-runtime-bad-unset"
  location = "us-central1"
  access_config {
    access_type = "SINGLE_USER"
    runtime_owner = "example@paloaltonetworks.com"
  }
  virtual_machine {
    virtual_machine_config {
      machine_type = "n1-standard-4"
      data_disk {
        initialize_params {
          disk_size_gb = "100"
          disk_type = "PD_STANDARD"
        }
      }
    }
  }
}