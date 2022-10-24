################
## PASS TESTS ##
################

resource "google_pubsub_topic_iam_binding" "pass1" {
  cluster = "my-private-topic-binding1"
  role    = "roles/pubsub.admin"
  members = [
    "user:jane@example.com",
    "group:mygroup@example.com",
  ]
}

resource "google_pubsub_topic_iam_binding" "pass2" {
  cluster = "my-private-topic-binding2"
  role    = "roles/pubsub.editor"
  members = [
    "user:jason@example.com",
  ]
}

resource "google_pubsub_topic_iam_member" "pass1" {
  cluster = "my-private-topic-member1"
  role    = "roles/pubsub.publisher"
  member  = "group:mygroup@example.com"
}

resource "google_pubsub_topic_iam_member" "pass2" {
  cluster = "my-private-topic-member2"
  role    = "roles/pubsub.subscriber"
  member  = "domain:example.com"
}


################
## FAIL TESTS ##
################

resource "google_pubsub_topic_iam_binding" "fail1" {
  cluster = "my-public-topic-binding1"
  role    = "roles/pubsub.viewer"
  members = [
    "allAuthenticatedUsers",
  ]
}

resource "google_pubsub_topic_iam_binding" "fail2" {
  cluster = "my-public-topic-binding2"
  role    = "roles/pubsub.admin"
  members = [
    "allUsers",
  ]
}

resource "google_pubsub_topic_iam_binding" "fail3" {
  cluster = "my-public-topic-binding3"
  role    = "roles/pubsub.editor"
  members = [
    "allUsers",
    "user:jason@example.com",
  ]
}

resource "google_pubsub_topic_iam_binding" "fail4" {
  cluster = "my-public-topic-binding4"
  role    = "roles/pubsub.publisher"
  members = [
    "user:jason@example.com",
    "allAuthenticatedUsers",
  ]
}

resource "google_pubsub_topic_iam_member" "fail1" {
  cluster = "my-public-topic-member1"
  role    = "roles/pubsub.subscriber"
  member  = "allAuthenticatedUsers"
}

resource "google_pubsub_topic_iam_member" "fail2" {
  cluster = "my-public-topic-member2"
  role    = "roles/pubsub.viewer"
  member  = "allUsers"
}
