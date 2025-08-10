resource "google_compute_instance_from_template" "fail1" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.default.id
  metadata {
    foo                    = "bar"
    hey                    = "oh"
    block-project-ssh-keys = false
  }
}

resource "google_compute_instance_from_template" "success1" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.default.id
  metadata = {
    foo                    = "bar"
    hey                    = "oh"
    block-project-ssh-keys = true
  }
}

resource "google_compute_instance_from_template" "success2" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.default.id
  metadata = {
    foo                    = "bar"
    hey                    = "oh"
    block-project-ssh-keys = "true"
  }
}

resource "google_compute_instance_from_template" "success3" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.default.id
  metadata = {
    foo                    = "bar"
    hey                    = "oh"
    block-project-ssh-keys = "True"
  }
}

resource "google_compute_instance_from_template" "success4" {
  name                     = "test"
  source_instance_template = google_compute_instance_template.default.id
  metadata = {
    foo                    = "bar"
    hey                    = "oh"
    block-project-ssh-keys = "TRUE"
  }
}