variable "project_id" {
  type        = string
  description = "ID del proyecto GCP"
}

variable "region" {
  type        = string
  description = "Región para los recursos (ej: us-central1)"
}

variable "api_url" {
  type        = string
  description = "URL base del endpoint GET que usará el servicio POST como DATA_API_URL"
}


variable "chatbot" {
  type        = string
  description = "Nombre del servicio Cloud Run para el chatbot"
}

variable "chatbot_url" {
  type        = string
  description = "Nombre del servicio Cloud Run para el chatbot"
}

variable "telegram" {
  type        = string
  description = "Nombre del servicio Cloud Run para el bot de Telegram"
  
}
