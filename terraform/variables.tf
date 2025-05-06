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