terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "8.9.0" }
  }
}

provider "google" {
  project      = "fake-project"
  region       = "us-central1"
  access_token = "fake-token"
}

resource "google_storage_bucket" "insecureBucket" {
  name     = "checkov-insecure-bucket"
  location = "US"
}

resource "google_storage_bucket" "secureBucket" {
  name                        = "checkov-secure-bucket"
  location                    = "US"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning {
    enabled = true
  }
  logging {
    log_bucket = "checkov-logs-bucket"
  }
}

resource "google_storage_bucket_iam_member" "publicBinding" {
  bucket = google_storage_bucket.insecureBucket.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_sql_database_instance" "sqlInstance" {
  name                = "checkov-sql"
  database_version    = "POSTGRES_15"
  region              = "us-central1"
  deletion_protection = false
  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
    database_flags {
      name  = "log_checkpoints"
      value = "off"
    }
  }
}

resource "google_compute_firewall" "firewall" {
  name          = "checkov-open-firewall"
  network       = "default"
  source_ranges = ["0.0.0.0/0"]
  allow {
    protocol = "tcp"
    ports    = ["22", "3389"]
  }
}

resource "google_compute_instance" "vm" {
  name           = "checkov-vm"
  machine_type   = "e2-micro"
  zone           = "us-central1-a"
  can_ip_forward = true
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }
  metadata = {
    serial-port-enable = "true"
  }
  service_account {
    email  = "123456789-compute@developer.gserviceaccount.com"
    scopes = ["cloud-platform"]
  }
}

resource "google_container_cluster" "cluster" {
  name                = "checkov-gke"
  location            = "us-central1"
  initial_node_count  = 1
  deletion_protection = false
  enable_legacy_abac  = true
  min_master_version  = "1.33"
  master_auth {
    client_certificate_config {
      issue_client_certificate = true
    }
  }
}

resource "google_kms_crypto_key" "key" {
  name            = "checkov-key"
  key_ring        = "projects/fake-project/locations/global/keyRings/checkov"
  rotation_period = "100000s"
}
