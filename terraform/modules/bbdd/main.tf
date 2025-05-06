resource "google_sql_database_instance" "instance" {
  name             = var.name_instance_bbdd
  region           = var.region
  database_version = var.db_version
  settings {
    tier = var.db_tier
  }

  deletion_protection  = false
}

resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.instance.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.instance.name
  password = var.db_password
}
