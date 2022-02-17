################
## PASS TESTS ##
################

resource "google_dataproc_cluster_iam_binding" "pass1" {
  cluster = "my-private-cluster-binding1"
  role    = "roles/dataproc.serviceAgent"
  members = [
    "user:jane@example.com",
    "group:mygroup@example.com",
  ]
}

resource "google_dataproc_cluster_iam_binding" "pass2" {
  cluster = "my-private-cluster-binding2"
  role    = "roles/dataproc.viewer"
  members = [
    "user:jason@example.com",
  ]
}

resource "google_dataproc_cluster_iam_member" "pass1" {
  cluster = "my-private-cluster-member1"
  role    = "roles/dataproc.worker"
  member  = "group:mygroup@example.com"
}

resource "google_dataproc_cluster_iam_member" "pass2" {
  cluster = "my-private-cluster-member2"
  role    = "roles/dataproc.editor"
  member  = "domain:example.com"
}


################
## FAIL TESTS ##
################

resource "google_dataproc_cluster_iam_binding" "fail1" {
  cluster = "my-public-cluster-binding1"
  role    = "roles/dataproc.hubAgent"
  members = [
    "allAuthenticatedUsers",
  ]
}

resource "google_dataproc_cluster_iam_binding" "fail2" {
  cluster = "my-public-cluster-binding2"
  role    = "roles/dataproc.editor"
  members = [
    "allUsers",
  ]
}

resource "google_dataproc_cluster_iam_binding" "fail3" {
  cluster = "my-public-cluster-binding3"
  role    = "roles/dataproc.editor"
  members = [
    "allUsers",
    "user:jason@example.com",
  ]
}

resource "google_dataproc_cluster_iam_binding" "fail4" {
  cluster = "my-public-cluster-binding4"
  role    = "roles/dataproc.editor"
  members = [
    "user:jason@example.com",
    "allUsers",
  ]
}

resource "google_dataproc_cluster_iam_member" "fail1" {
  cluster = "my-public-cluster-member1"
  role    = "roles/dataproc.admin"
  member  = "allAuthenticatedUsers"
}

resource "google_dataproc_cluster_iam_member" "fail2" {
  cluster = "my-public-cluster-member2"
  role    = "roles/editor"
  member  = "allUsers"
}
