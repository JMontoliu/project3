resource "google_project_service" "bigquery" {
  project                    = var.project_id
  service                    = "bigquery.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset
  project    = var.project_id
  depends_on = [google_project_service.bigquery]
}

resource "google_bigquery_table" "table" {
  for_each  = { for t in var.tables : t.name => t }
  
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = each.value.name
  project    = var.project_id
  schema = file("${path.module}/schemas/${each.value.schema}")
  deletion_protection  = false  
  depends_on          = [google_bigquery_dataset.dataset]
}

resource "google_project_service" "firestore" {
  project                    = var.project_id
  service                    = "firestore.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false 
}

resource "google_firestore_database" "database" {
  project                     = var.project_id
  name                        = var.firestore_database_name
  location_id                 = var.region 
  type                        = "FIRESTORE_NATIVE" 
  app_engine_integration_mode = "DISABLED"     

  depends_on = [google_project_service.firestore]
}
