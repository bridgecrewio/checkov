
# Passes due to ip_configuration" existing and set to private
resource "google_dataflow_job" "pass" {
  name              = "my-pass-job"
  template_gcs_path = "gs://my-bucket/templates/template_file"
  temp_gcs_location = "gs://my-bucket/tmp_dir"
  parameters = {
    foo = "bar"
    baz = "qux"
  }

  ip_configuration = "WORKER_IP_PRIVATE"
}


# Fails due to "ip_configuration" not existing
# Dataflow jobs are public by default
resource "google_dataflow_job" "fail1" {
  name              = "my-fail-job1"
  template_gcs_path = "gs://my-bucket/templates/template_file"
  temp_gcs_location = "gs://my-bucket/tmp_dir"
  parameters = {
    foo = "bar"
    baz = "qux"
  }

}

# Fails due to "ip_configuration" existing but set to public
resource "google_dataflow_job" "fail2" {
  name              = "my-fail-job2"
  template_gcs_path = "gs://my-bucket/templates/template_file"
  temp_gcs_location = "gs://my-bucket/tmp_dir"
  parameters = {
    foo = "bar"
    baz = "qux"
  }

  ip_configuration = "WORKER_IP_PUBLIC"
}
