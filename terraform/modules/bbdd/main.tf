# Crear el dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset
  project    = var.project_id
}

# Crear múltiples tablas con su respectivo esquema
resource "google_bigquery_table" "table" {
  for_each  = { for t in var.tables : t.name => t }
  
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = each.value.name
  project    = var.project_id
  schema = file("${path.module}/schemas/${each.value.schema}")
  deletion_protection  = false  
}

resource "google_project_service" "sqladmin" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
  
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_sql_database_instance" "postgres" {
  name             = var.postgres_instance_name
  database_version = "POSTGRES_14"
  region           = var.region
  project          = var.project_id
  
  settings {
    tier = var.postgres_tier

  }
  
  deletion_protection = false
}

resource "google_sql_database" "database" {
  name     = var.postgres_db_name
  instance = google_sql_database_instance.postgres.name
  project  = var.project_id
}

resource "google_sql_user" "user" {
  name     = var.postgres_user
  instance = google_sql_database_instance.postgres.name
  password = var.postgres_password
  project  = var.project_id
}
