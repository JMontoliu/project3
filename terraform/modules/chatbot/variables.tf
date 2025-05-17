variable "project_id" {
  description = "ID del proyecto GCP"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
}

variable "image_name" {
  description = "Nombre de la imagen Docker"
  type        = string
}

variable "cloud_run_service_name" {
  description = "Nombre del servicio en Cloud Run"
  type        = string
}

variable "db_host" {
  description = "Host de la base de datos (Cloud SQL)"
  type        = string
}

variable "port" {
  description = "Puerto de conexión a la base de datos"
  type        = string
}

variable "db_name" {
  description = "Nombre de la base de datos"
  type        = string
}

variable "db_user" {
  description = "Usuario de la base de datos"
  type        = string
}

variable "db_password" {
  description = "Contraseña del usuario de la base de datos"
  type        = string
}
