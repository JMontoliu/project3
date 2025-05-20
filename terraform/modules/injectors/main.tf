resource "null_resource" "update-api-agent" {

  provisioner "local-exec" {
      command = <<EOT
      gcloud run services update ${var.chatbot} --region=${var.region} --project=${var.project_id} --update-env-vars=COSTUMER_API_URL=${var.api_url}
  EOT
    }
}

# resource "null_resource" "chatbot_url_telegram" {

#   provisioner "local-exec" {
#       command = <<EOT
#       gcloud run services update ${var.telegram} --region=${var.region} --project=${var.project_id} --update-env-vars=URL_CHATBOT=${var.chatbot_url}
#   EOT
#     }
# }

resource "null_resource" "chatbot_url_streamlit" {

  provisioner "local-exec" {
      command = <<EOT
      gcloud run services update ${var.streamlit} --region=${var.region} --project=${var.project_id} --update-env-vars=URL_CHATBOT2=${var.chatbot_url}
  EOT
    }
}