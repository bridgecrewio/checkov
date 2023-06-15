resource "google_compute_instance" "bad" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  boot_disk {}
}

resource "google_compute_instance" "good" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  boot_disk {
    disk_encryption_key_raw = "acXTX3rxrKAFTF0tYVLvydU1riRZTvUNC4g5I11NY-c="  # checkov:skip=CKV_SECRET_6 test secret
  }
}

resource "google_service_account" "default" {
  account_id   = "service_account_id"
  display_name = "Service Account"
}

resource "google_compute_instance" "bad2" {
  name         = "test"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  tags = ["foo", "bar"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      labels = {
        my_label = "value"
      }
    }
  }

  // Local SSD disk
  scratch_disk {
    interface = "SCSI"
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    foo = "bar"
  }

  metadata_startup_script = "echo hi > /test.txt"

  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = google_service_account.default.email
    scopes = ["cloud-platform"]
  }
}