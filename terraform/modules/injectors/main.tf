resource "null_resource" "update-api-agent" {

  provisioner "local-exec" {
      command = <<EOT
      gcloud run services update ${var.chatbot} --region=${var.region} --project=${var.project_id} --update-env-vars=COSTUMER_API_URL=${var.api_url}
  EOT
    }
}

resource "null_resource" "chatbot_url" {

  provisioner "local-exec" {
      command = <<EOT
      gcloud run services update ${var.telegram} --region=${var.region} --project=${var.project_id} --update-env-vars=URL_CHATBOT=${var.chatbot_url}
  EOT
    }
}