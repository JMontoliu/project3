variable project_id {
  type        = string
  default     = "dataproject03"
  description = "GCP project ID"
}

variable region {
  type        = string
  default     = "europe-west1"
  description = "General region for all resources"
}

variable tf_state_bucket_name {
  type        = string
  default     = "tfstate-chatbot-dp03"
  description = "Name of the bucket for terraform state"
}


variable name_instance_bbdd {
  type        = string
  default     = "database-instance-chatbot"
  description = "Name of the instance"
}

variable db_tier {
  type        = string
  default     = "db-f1-micro"
  description = "Database tier"
}

variable db_version {
  type        = string
  default     = "POSTGRES_15"
  description = "Database version"
}

variable db_name {
  type        = string
  default     = "db-chatbot"
  description = "Name of the database"
}

variable db_user {
  type        = string
  default     = "admin"
  description = "Database user"
}

variable db_password {
  type        = string
  default     = "admin"
  description = "Database password"
}

variable topic_name {
  description = "The name of the Pub/Sub topic"
  type        = string
    default     = "chatbot-topic"
}

variable subscription_name {
  description = "The name of the Pub/Sub subscription"
  type        = string
    default     = "chatbot-subscription"
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

variable "image_name" {
  description = "Nombre de la imagen Docker"
  type        = string

}

variable "cloud_run_service_name" {
  description = "Nombre del servicio en Cloud Run"
  type        = string

}

variable "db_host" {
  description = "Host de la base de datos (IP o conexión Cloud SQL Proxy)"
  type        = string

}

variable "port" {
  description = "Puerto de conexión a la base de datos"
  type        = string

}
