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
    schema = string  # Ruta relativa al módulo
  }))
}
