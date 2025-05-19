variable "project_id" {
  description = "ID del proyecto GCP"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
}

variable "repository_name3" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
  
}

variable "image_name3" {
  description = "Nombre de la imagen Docker"
  type        = string
  
}

variable "cloud_run_service_name3" {
  description = "Nombre del servicio en Cloud Run"
  type        = string
  
}

variable "url_chatbot" {
    description = "URL del servicio de chatbot"
    type        = string    
  
}

variable "telegram_api_key" {
  description = "Clave de API de Telegram"
  type        = string
}