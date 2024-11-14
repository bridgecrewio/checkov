resource "google_compute_instance" "fail1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
}

resource "google_compute_instance" "fail2" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  metadata = {
    block-project-ssh-keys = false
  }
}

resource "google_compute_instance" "success1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  metadata = {
    block-project-ssh-keys = true
  }
}

resource "google_compute_instance" "success2" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  metadata = {
    block-project-ssh-keys = "true"
  }
}

resource "google_compute_instance" "success3" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  metadata = {
    block-project-ssh-keys = "True"
  }
}

resource "google_compute_instance" "success4" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  metadata = {
    block-project-ssh-keys = "TRUE"
  }
}