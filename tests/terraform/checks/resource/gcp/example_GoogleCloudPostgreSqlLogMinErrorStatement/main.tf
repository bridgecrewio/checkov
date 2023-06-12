resource "google_sql_database_instance" "fail" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_min_error_statement"
      value = "log"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "fail2" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_min_error_statement"
      value = "fatal"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "fail3" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_min_error_statement"
      value = "panic"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "pass" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_min_error_statement"
      value = "info"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "unknown" {
  name             = "db"
  database_version = "MYSQL_5_6"
  region           = "us-central1"
  settings {
    database_flags {
      name  = "local_infile"
      value = "on"
    }
    tier = "db-custom-1-3840"
  }
}
