resource "google_project_service" "firestore" {
  project = var.project_id
  service = "firestore.googleapis.com"
}

resource "google_firestore_database" "customers" {
  project     = var.project_id
  name        = "customers"
  location_id = var.location
  type        = "FIRESTORE_NATIVE"
}
