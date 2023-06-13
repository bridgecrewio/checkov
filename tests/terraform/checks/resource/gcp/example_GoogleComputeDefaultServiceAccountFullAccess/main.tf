resource "google_compute_instance" "fail1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
  }
}

resource "google_compute_instance" "fail2" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance_template" "fail3" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance_from_template" "fail4" {
  name         = "test"
  source_instance_template = google_compute_instance_template.tpl.id

  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance" "fail5" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["cloud-platform"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance" "pass1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email  = "example@email.com"
  }
}

resource "google_compute_instance" "pass2" {
  name         = "gke-account"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["https://www.googleapis.com/auth/cloud-platform", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance" "broken" {
}

resource "google_compute_instance_from_template" "unknown1" {
  name         = "test"
  source_instance_template = google_compute_instance_template.tpl.id
}
