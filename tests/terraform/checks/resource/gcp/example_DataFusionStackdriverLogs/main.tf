resource "google_data_fusion_instance" "pass" {
  project                       = "examplea"
  provider                      = google-beta
  name                          = "my-instance"
  description                   = "My Data Fusion instance"
  region                        = "us-central1"
  type                          = "BASIC"
   enable_stackdriver_logging    = true
   enable_stackdriver_monitoring = true
  labels = {
    example_key = "example_value"
  }
  //private_instance = false
  network_config {
    network       = "default"
    ip_allocation = "10.89.48.0/22"
  }
  version                  = "6.3.0"
  dataproc_service_account = data.google_app_engine_default_service_account.default.email
}
resource "google_data_fusion_instance" "fail" {
  project                       = "examplea"
  provider                      = google-beta
  name                          = "my-instance"
  description                   = "My Data Fusion instance"
  region                        = "us-central1"
  type                          = "BASIC"
  labels = {
    example_key = "example_value"
  }
  //private_instance = false
  network_config {
    network       = "default"
    ip_allocation = "10.89.48.0/22"
  }
  version                  = "6.3.0"
  dataproc_service_account = data.google_app_engine_default_service_account.default.email
}
resource "google_data_fusion_instance" "fail2" {
  project                       = "examplea"
  provider                      = google-beta
  name                          = "my-instance"
  description                   = "My Data Fusion instance"
  region                        = "us-central1"
  type                          = "BASIC"
   enable_stackdriver_logging    = false
   enable_stackdriver_monitoring = false
  labels = {
    example_key = "example_value"
  }
  //private_instance = false
  network_config {
    network       = "default"
    ip_allocation = "10.89.48.0/22"
  }
  version                  = "6.3.0"
  dataproc_service_account = data.google_app_engine_default_service_account.default.email
}