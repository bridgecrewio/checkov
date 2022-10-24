resource "google_cloudbuild_worker_pool" "fail" {
  name = "my-pool"
  location = "europe-west1"
  worker_config {
    disk_size_gb = 100
    machine_type = "e2-standard-4"
    no_external_ip = false
  }
}

resource "google_cloudbuild_worker_pool" "fail2" {
  name = "my-pool"
  location = "europe-west1"
  worker_config {
    disk_size_gb = 100
    machine_type = "e2-standard-4"
  }
}

resource "google_cloudbuild_worker_pool" "pass" {
  name = "my-pool"
  location = "europe-west1"
  worker_config {
    disk_size_gb = 100
    machine_type = "e2-standard-4"
    no_external_ip = true
  }
}