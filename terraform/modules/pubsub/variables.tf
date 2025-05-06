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