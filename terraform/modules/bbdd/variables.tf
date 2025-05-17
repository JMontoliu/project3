variable "project_id" {
  type        = string
  description = "ID del proyecto GCP"
}

variable "bq_dataset" {
  type        = string
  description = "ID del dataset de BigQuery"
}

variable "tables" {
  description = "Lista de tablas con su esquema JSON"
  type = list(object({
    name   = string
    schema = string  
  }))
}

variable "region" {
  type        = string
  description = "Región de GCP"
}

variable "firestore_database_name" {
  description = "El nombre de la base de datos Firestore."
  type        = string
  default     = "customers"
}