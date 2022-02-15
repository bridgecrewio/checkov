
resource "google_compute_project_metadata" "fail" {
  metadata = {
    foo = "bar"
  }
}
resource "google_compute_project_metadata" "pass" {
  metadata = {
    foo            = "bar"
    enable-oslogin = "TRUE"
  }
}

resource "google_compute_project_metadata_item" "ignores" {
  key   = "enable-osconfig"
  value = "TRUE"
}