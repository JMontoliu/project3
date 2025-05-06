variable "project_id" {
  description = "Project ID de GCP"
  type        = string
}

variable "location" {
  description = "Region for resources"
  type        = string
  default     = "europe-west1"
}

variable "topics" {
  description = "List of Pub/Sub topics"
  type        = list(string)
  default     = ["customers", "business"]
}

variable "function_name" {
  description = "Name of the Cloud Function"
  type        = string
  default     = "pubsub_listener"
}
