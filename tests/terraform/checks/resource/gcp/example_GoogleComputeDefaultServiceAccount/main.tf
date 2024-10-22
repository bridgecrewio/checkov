#resource "google_compute_instance" "fail1" {
#  name         = "test"
#  machine_type = "n1-standard-1"
#  zone         = "us-central1-a"
#}

resource "google_compute_instance" "fail2" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance_from_template" "fail3" {
  name                     = "instance_from_template"
  source_instance_template = google_compute_instance_template.default.id
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance_from_template" "unknown1" {
  name                     = "instance_from_template"
  source_instance_template = google_compute_instance_template.default.id
}

resource "google_compute_instance" "pass1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  = "example@email.com"
  }
}

resource "google_compute_instance" "pass2" {
  name         = "gke-account"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  =  "123456789-compute@developer.gserviceaccount.com"
  }
}

resource "google_compute_instance_template" "pass3" {
  name         = "account"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  = "example@email.com"
  }
}

resource "google_compute_instance_from_template" "pass4" {
  name                     = "instance_from_template"
  source_instance_template = google_compute_instance_template.default.id
  service_account {
    scopes = ["userinfo-email", "compute-ro", "storage-ro"]
    email  = "example@email.com"
  }
}

resource "google_compute_instance" "unknown2" {
  name         = "my-instance"
  machine_type = "n2-standard-2"
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
    interface = "NVME"
  }

  network_interface {
    network = "vpc-test"
    subnetwork = "private-subnet-01-test"
  }

  metadata = {
    foo = "bar"
  }


}
