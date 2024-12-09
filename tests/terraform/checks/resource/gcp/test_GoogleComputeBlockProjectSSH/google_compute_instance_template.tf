resource "google_compute_instance_template" "fail1" {
  name         = "test"
  machine_type = "e2-medium"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  can_ip_forward = true
}

resource "google_compute_instance_template" "fail2" {
  name         = "test"
  machine_type = "e2-medium"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  metadata = {
    foo = "bar"
  }

  can_ip_forward = true
}

resource "google_compute_instance_template" "success1" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  can_ip_forward = true
  metadata = {
    foo                    = "bar",
    block-project-ssh-keys = true
  }
}

resource "google_compute_instance_template" "success2" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  can_ip_forward = true
  metadata = {
    foo                    = "bar",
    block-project-ssh-keys = "true"
  }
}

resource "google_compute_instance_template" "success3" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  can_ip_forward = true
  metadata = {
    foo                    = "bar",
    block-project-ssh-keys = "True"
  }
}

resource "google_compute_instance_template" "success4" {
  name         = "test"
  machine_type = "n1-standard-1"
  zone         = "us-central1-a"

  disk {
    source_image = "debian-cloud/debian-9"
    auto_delete  = true
    disk_size_gb = 100
    boot         = true
  }

  network_interface {
    network = "default"
  }

  can_ip_forward = true
  metadata = {
    foo                    = "bar",
    block-project-ssh-keys = "TRUE"
  }
}