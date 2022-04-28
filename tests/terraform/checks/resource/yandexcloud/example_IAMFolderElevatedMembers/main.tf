# pass
resource "yandex_resourcemanager_folder_iam_binding" "pass-1" {
  role = "alb.viewer"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_resourcemanager_folder_iam_member" "pass-2" {
  role   = "k8s.admin"
  member = "userAccount:user_id"
}

# fail
resource "yandex_resourcemanager_folder_iam_binding" "fail-1" {
  role = "admin"
  members = [
    "userAccount:some_user_id",
  ]
}

resource "yandex_resourcemanager_folder_iam_member" "fail-2" {
  role   = "editor"
  member = "userAccount:user_id"
}