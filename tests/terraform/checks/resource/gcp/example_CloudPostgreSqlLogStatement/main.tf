
resource "google_sql_database_instance" "fail" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_statement"
      value = "none"
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
      name  = "log_statement"
      value = "ddl"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "pass2" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_statement"
      value = "mod"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "pass3" {
  database_version = "POSTGRES_15"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_statement"
      value = "all"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
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
