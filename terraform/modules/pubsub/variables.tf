variable "topics" {
  description = "Lista de nombres de los topics de Pub/Sub"
  type        = list(string)
}

variable "project_id" {
  description = "Project ID de GCP"
  type        = string
}
