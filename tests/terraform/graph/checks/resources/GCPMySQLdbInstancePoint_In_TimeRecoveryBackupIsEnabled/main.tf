#PASS case 1: 
resource "google_sql_database_instance" "pass_1" {
  name             = "pud_pass_sqldb"
  database_version = "MYSQL_5_7"

  deletion_protection = false
  settings {
    tier = "db-f1-micro"

    backup_configuration {
      binary_log_enabled = "true"
    }
  }
}

#PASS case 2: database_version is not starting with "MYSQL_"
resource "google_sql_database_instance" "pass_2" {
  name             = "pud_sqldb"
  database_version = "POSTGRES_15"

  deletion_protection = false
  settings {
    tier = "db-f1-micro"

    backup_configuration {
      binary_log_enabled = "true"
    }
  }
}

#FAIL case 3: binary_log_enabled is not True
resource "google_sql_database_instance" "fail" {
  name             = "pud_sqldb"
  database_version = "MYSQL_5_7"

  deletion_protection = false
  settings {
    tier = "db-f1-micro"

    backup_configuration {
      binary_log_enabled = "false"
    }
  }
}

# Pass: replicas can't have point in time recovery
resource "google_sql_database_instance" "replica" {
  name                 = "${google_sql_database_instance.default.name}-replica"
  database_version     = google_sql_database_instance.default.database_version
  region               = google_sql_database_instance.default.region
  project              = google_sql_database_instance.default.project
  master_instance_name = google_sql_database_instance.default.name

  settings {
    tier      = var.cloudsql_replica_machine_type
    disk_size = 40
    ip_configuration {
      ipv4_enabled    = true
      private_network = data.google_compute_network.default.id
    }
    database_flags {
      name  = "innodb_lock_wait_timeout"
      value = "240"
    }
    backup_configuration {
      enabled                        = true
      location                       = "eu"
      start_time                     = "04:42"
      backup_retention_settings {
        retention_unit   = "COUNT"
        retained_backups = 7
      }
    }
  }
  deletion_protection = true
}