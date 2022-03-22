resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_sql_database_instance" "db_instance_good_1" {
  name = "master-instance-${random_id.db_name_suffix.hex}"
  database_version = "MYSQL_8_0"

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database_instance" "db_instance_good_2" {
  name = "master-instance-${random_id.db_name_suffix.hex}"
  database_version = "MYSQL_8_0"

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database_instance" "db_instance_good_3_no_pass" {
  name = "master-instance-${random_id.db_name_suffix.hex}"
  database_version = "POSTGRES_13"

  settings {
    tier = "db-f1-micro"
  }
}


resource "google_sql_database_instance" "db_instance_bad" {
  name = "master-instance-${random_id.db_name_suffix.hex}"
  database_version = "MYSQL_8_0"

  settings {
    tier = "db-f1-micro"
  }
}


resource "google_sql_user" "root_good" {
  name     = "root"
  instance = google_sql_database_instance.db_instance_good_1.name
  host     = "me.com"
  password = "1234"
}

resource "google_sql_user" "root_good_3" {
  name     = "root"
  instance = google_sql_database_instance.db_instance_good_3_no_pass.name
  host     = "me.com"
}

resource "google_sql_user" "root_bad" {
  name     = "root@#"
  instance = google_sql_database_instance.db_instance_bad.name
  host     = "me.com"
}

