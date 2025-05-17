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
  description = "Región para desplegar los recursos"
  default     = "europe-west1"
}

variable "postgres_instance_name" {
  type        = string
  description = "Nombre de la instancia de Cloud SQL PostgreSQL"
  default     = "postgres-instance"
}

variable "postgres_tier" {
  type        = string
  description = "Tier para la instancia de Cloud SQL"
  default     = "db-f1-micro"
}

variable "postgres_db_name" {
  type        = string
  description = "Nombre de la base de datos PostgreSQL"
  default     = "customers"
}

variable "postgres_user" {
  type        = string
  description = "Usuario para la base de datos PostgreSQL"
}

variable "postgres_password" {
  type        = string
  description = "Contraseña para el usuario de PostgreSQL"
  sensitive   = true
}