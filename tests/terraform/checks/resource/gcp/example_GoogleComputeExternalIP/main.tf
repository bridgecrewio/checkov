
resource "google_compute_instance" "fail" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  boot_disk {
    auto_delete = true
  }

  network_interface {
    network = "default"
    access_config {
    }
  }
}


resource "google_compute_instance_template" "fail" {
  name         = "test"
  machine_type = "n1-standard-1"

  disk {}
  network_interface {
    network = "default"
    access_config {

    }
  }
}


resource "google_compute_instance_from_template" "fail" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.pass.id
}

resource "google_compute_instance" "pass" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  boot_disk {
    auto_delete = true
  }
  network_interface {

  }
}

resource "google_compute_instance_template" "pass" {
  name         = "test"
  machine_type = "n1-standard-1"
  disk {}
}

resource "google_compute_instance_from_template" "unknown" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.pass.id
}

