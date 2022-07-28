resource "google_project" "project_good_1" {
  name = "good1"
  project_id = "123456"
}

resource "google_project" "project_good_2" {
  name = "good2"
  project_id = "123456"
}

resource "google_project" "project_bad_1" {
  name = "bad1"
  project_id = "123456"
}

resource "google_project" "project_bad_2" {
  name = "bad2"
  project_id = "123456"
}

resource "google_project" "project_bad_3" {
  name = "bad3"
  project_id = "123456"
}

resource "google_project_iam_audit_config" "project_good_audit_2" {
  project = google_project.project_good_1.id
  service = "allServices"
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
}

resource "google_project_iam_audit_config" "project_good_audit_2" {
  project = google_project.project_good_2.id
  service = "allServices"
  audit_log_config {
    exempted_members = []
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    exempted_members = []
    log_type = "DATA_READ"
  }
}

resource "google_project_iam_audit_config" "project_bad_audit_1" {
  project = google_project.project_bad_1.id
  service = "allServices"
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
    exempted_members = [
      "user:joebloggs@hashicorp.com",
    ]
  }
}

resource "google_project_iam_audit_config" "project_bad_audit_2" {
  project = google_project.project_bad_2.id
  service = "someService"
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  audit_log_config {
    log_type = "DATA_READ"
  }
}
