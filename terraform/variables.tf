variable project_id {
  type        = string
  description = "GCP project ID"
}

variable region {
  type        = string
  description = "General region for all resources"
}

variable tf_state_bucket_name {
  type        = string
  default     = "tfstate-chatbot-dp03"
  description = "Name of the bucket for terraform state"
}

variable db_name {
  type        = string
  default     = "customers"
  description = "Name of the database"
}

variable db_user {
  type        = string
  default     = "admin"
  description = "Database user"
}

variable "postgres_db_name" {
  type        = string
  description = "Nombre de la base de datos PostgreSQL"
  default     = "customers"
}

variable "postgres_password" {
  type        = string
  description = "Contraseña para el usuario de PostgreSQL"
  default = "admin"
}

variable db_password {
  type        = string
  default     = "admin"
  description = "Database password"
}

variable topic {
  description = "The name of the Pub/Sub topic"
  type        = string
  default     = "chatbot-topic"
}

variable subscription_labels {
  description = "Labels for the Pub/Sub subscription"
  type        = map(string)
  default     = {}
}

variable "push_endpoint" {
  type        = string
  default     = null
  description = "Endpoint HTTP(S) al que se enviarán los mensajes si se usa una suscripción push"
}

variable "repository_name" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string

}

variable "repository_name2" {
  description = "Nombre del repositorio en Artifact Registry"
  type        = string

}

variable "image_name" {
  description = "Nombre de la imagen Docker"
  type        = string

}

variable "image_name2" {
  description = "Nombre de la imagen Docker"
  type        = string

}

variable "cloud_run_service_name" {
  description = "Nombre del servicio en Cloud Run"
  type        = string

}

variable "cloud_run_service_name2" {
  description = "Nombre del servicio en Cloud Run"
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

variable "port" {
  description = "Puerto de conexión a la base de datos"
  type        = string

}

variable "bq_dataset" {
  type        = string
  description = "Nombre del dataset de BigQuery"
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

variable "entry_point" {
  type        = string
  description = "Nombre de la función que se ejecuta al recibir un mensaje"
  default = "process_pubsub_message"
  
}

variable "name" {
  type        = string
  description = "Nombre de la función"
  default     = "insert_data_function"
}

variable "google_api_key" {
  description = "Clave de API de Google"
  type        = string
}

variable "api_weather_key" {
  description = "Clave de API de WeatherAPI"
  type        = string
}

variable "telegram_api_key" {
  description = "URL de la API"
  type        = string
}