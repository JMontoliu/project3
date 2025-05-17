variable "project_id" {
  type        = string
  description = "ID del proyecto de GCP"
}

variable "region" {
  type        = string
  description = "Región donde se desplegará la función"
}


variable "topic" {
  type        = string
  description = "Nombre del topic de Pub/Sub que dispara la función"
}

variable "env_variables" {
  type        = map(string)
  default     = {}
  description = "Variables de entorno para la función"
}

variable "entry_point" {
  type        = string
  description = "Nombre de la función que se ejecuta al recibir un mensaje"
  
}

variable "name" {
  type        = string
  description = "Nombre de la función"
}