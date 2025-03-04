resource "google_notebooks_instance" "fail" {
  name       = "notebook-instance-pass"
  location   = "us-central1-a"
  machine_type = "n1-standard-4"

  shielded_instance_config {
    enable_vtpm               = false
    enable_integrity_monitoring = false
  }

  // Additional configuration as needed...
}

resource "google_notebooks_instance" "pass" {
  name       = "notebook-instance-fail"
  location   = "us-central1-a"
  machine_type = "n1-standard-4"

  shielded_instance_config {
    enable_vtpm               = true
    enable_integrity_monitoring = false
  }

  // Additional configuration as needed...
}
