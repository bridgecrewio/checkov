resource "google_cloud_run_v2_job" "example" {
  name     = "cloudrun-job"
  location = "us-central1"
  launch_stage = "BETA"

  template {
    template {
      containers {
        image = "gcr.io/cloudrun/job"
      }
    }
  }
}

resource "google_cloud_run_v2_service" "example" {
  name     = "cloudrun-service"
  location = "us-central1"
  ingress = "INGRESS_TRAFFIC_ALL"

  binary_authorization {
    use_default = true
    breakglass_justification = "Some justification"
  }
  template {
    containers {
      image = "gcr.io/cloudrun/hello"
    }
  }
}
