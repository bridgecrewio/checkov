# pass

resource "google_bigquery_dataset" "pass_special_group" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role          = "READER"
    special_group = "projectReaders"
  }
}

resource "google_bigquery_dataset" "pass_user_by_email" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role          = "EDITOR"
    user_by_email = "foo@bar.com"
  }
}

resource "google_bigquery_dataset" "pass_group_by_email" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role           = "EDITOR"
    group_by_email = "foo-team@bar.com"
  }
}

resource "google_bigquery_dataset" "pass_domain" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role   = "EDITOR"
    domain = "example.com"
  }
}

resource "google_bigquery_dataset" "pass_view" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    view {
      dataset_id = "bar"
      project_id = "foo"
      table_id   = "buzz"
    }
  }
}

resource "google_bigquery_dataset" "pass_routine" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    routine {
      dataset_id = "bar"
      project_id = "foo"
      routineId  = "buzz"
    }
  }
}

resource "google_bigquery_dataset" "pass_dataset" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    dataset {
      target_types = ["VIEWS"]
      dataset {
        dataset_id = "foo"
        project_id = "bar"
      }
    }
  }
}

# fail

resource "google_bigquery_dataset" "fail_special_group" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role          = "READER"
    special_group = "allAuthenticatedUsers"
  }
}

resource "google_bigquery_dataset" "fail_all_users" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role          = "VIEWER"
    special_group = "projectReaders"
  }
  access {
    role = "READER"
  }
}

resource "google_bigquery_dataset" "fail_new_key" {
  dataset_id                  = "example_dataset"
  friendly_name               = "test"
  description                 = "This is a test description"
  location                    = "US"

  access {
    role    = "READER"
    new_key = "new_value"  # this test a possible new addition
  }
}
