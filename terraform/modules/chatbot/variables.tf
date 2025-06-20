variable "project_id" {
  description = "ID del proyecto GCP"
  type        = string
}

variable "region" {
  description = "Región de despliegue"
  type        = string
}

variable "repository_name2" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string
  
}

variable "image_name2" {
  description = "Nombre de la imagen Docker"
  type        = string
  
}

variable "cloud_run_service_name2" {
  description = "Nombre del servicio en Cloud Run"
  type        = string
  
}

variable "url_api" {
  description = "URL de la API"
  type        = string
  
}

variable "google_api_key" {
  description = "Clave de API de Google"
  type        = string
}

variable "api_weather_key" {
  description = "Clave de API de WeatherAPI"
  type        = string
}