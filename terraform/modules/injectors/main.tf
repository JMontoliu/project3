resource "null_resource" "update-api-agent" {

  provisioner "local-exec" {
      command = <<EOT
      gcloud run services update ${var.chatbot} --region=${var.region} --project=${var.project_id} --update-env-vars=POST_API_URL=${var.api_url}
  EOT
    }
}