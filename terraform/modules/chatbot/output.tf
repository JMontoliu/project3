output "env_vars_api" {
  description = "API name"
  value       = google_cloud_run_v2_service.chatbot.name
}

output "url_chatbot" {
  description = "URL API"
  value       = google_cloud_run_v2_service.chatbot.uri
}