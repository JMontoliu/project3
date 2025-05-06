variable "project_id" {
  description = "Project ID de GCP"
  type        = string
}

variable "location" {
  description = "Location for Firestore database"
  type        = string
  default     = "europe-southwest1"
}
