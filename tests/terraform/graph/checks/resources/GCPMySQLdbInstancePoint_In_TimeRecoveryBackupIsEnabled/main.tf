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
