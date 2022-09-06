resource "google_cloudfunctions_function_iam_member" "pass" {
  project        = google_cloudfunctions_function.pikey.project
  region         = google_cloudfunctions_function.pikey.region
  cloud_function = google_cloudfunctions_function.pikey.name

  role   = "roles/cloudfunctions.invoker"
  member = "user:james.woolfenden@gmail.com"
}

resource "google_cloudfunctions_function_iam_member" "fail" {
  project        = google_cloudfunctions_function.pikey.project
  region         = google_cloudfunctions_function.pikey.region
  cloud_function = google_cloudfunctions_function.pikey.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

resource "google_cloudfunctions_function" "pikey" {

  docker_registry              = "CONTAINER_REGISTRY"
  entry_point                  = "helloWorld"
  environment_variables        = {}
  https_trigger_security_level = "SECURE_ALWAYS"
  https_trigger_url            = "https://europe-west2-pike-361314.cloudfunctions.net/pikey"
  labels = {
    deployment-tool = "console-cloud"
    tag             = "deployment-tool"
    pike            = "permissions"
  }
  max_instances         = 3000
  min_instances         = 0
  name                  = "pikey"
  project               = "pike-361314"
  region                = "europe-west2"
  runtime               = "nodejs16"
  service_account_email = "pike-361314@appspot.gserviceaccount.com"
  trigger_http          = true
}
