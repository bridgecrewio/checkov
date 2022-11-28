
resource "google_sql_database_instance" "fail" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "off"
    }
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
    }
    pricing_plan = "PER_USE"

    tier = "db-custom-1-3840"
  }
}


resource "google_sql_database_instance" "fail2" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags {
      name  = "log_checkpoints"
      value = "off"
    }
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
  }
}

resource "google_sql_database_instance" "pass" {
  database_version = "POSTGRES_12"
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
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_min_messages"
      value = "debug6"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_temp_files"
      value = "10"
    }
    database_flags {
      name  = "log_min_duration_statement"
      value = "1"
    }
    pricing_plan = "PER_USE"
    tier         = "db-custom-1-3840"
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

resource "google_sql_database_instance" "unknown_var" {
  database_version = "POSTGRES_12"
  name             = "general-pos121"
  project          = "gcp-bridgecrew-deployment"
  region           = "us-central1"
  settings {
    activation_policy = "ALWAYS"
    availability_type = "ZONAL"
    database_flags = ["${var.test_var}"]
    tier = "db-custom-1-3840"
  }
}