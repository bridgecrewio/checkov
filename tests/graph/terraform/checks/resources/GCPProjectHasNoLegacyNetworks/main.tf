resource "google_project" "project_good_1" {
  name       = "My Project"
  project_id = "good"
  org_id     = "1234567"
}

resource "google_project" "project_good_2" {
  name       = "My Project"
  project_id = "good"
  org_id     = "1234567"
}

resource "google_project" "project_bad_1" {
  name       = "My Project"
  project_id = "bad"
  org_id     = "1234567"
}

resource "google_compute_network" "vpc_network_network" {
  name = "vpc-legacy"
  auto_create_subnetworks = true
  project = google_project.project_bad_1.id
}

resource "google_compute_network" "vpc_network_1" {
  name = "vpc-legacy"
  project = google_project.project_good_1.id
}

resource "google_compute_network" "vpc_network_2" {
  name = "vpc-legacy"
  project = google_project.project_good_1.id
  auto_create_subnetworks = false
}