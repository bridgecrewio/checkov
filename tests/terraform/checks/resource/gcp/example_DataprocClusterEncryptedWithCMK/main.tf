resource "google_dataproc_cluster" "fail" {
  name   = "simplecluster"
  region = "us-central1"
  cluster_config {
    # encryption_config{
    #   kms_key_name="SecretSquirrel"
    # }
  }
}

resource "google_dataproc_cluster" "pass" {
  name   = "simplecluster"
  region = "us-central1"
  cluster_config {
     encryption_config{
       kms_key_name="SecretSquirrel"
     }
  }
}