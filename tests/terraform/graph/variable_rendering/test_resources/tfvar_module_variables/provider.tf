provider "google" {
  credentials = "${file("${var.path}/account.json")}" // put the path to your service account file
  project     = "airpods-yoyo-291302"
  region      = "us-central1-a"
}
