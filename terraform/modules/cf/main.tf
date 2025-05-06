resource "google_pubsub_topic" "topics" {
  for_each = toset(var.topics)

  name    = each.value
  project = var.project_id
}

resource "google_storage_bucket_object" "function_code" {  #para subir el zup q contiene el codigo a un bucket
  name   = "function.zip"
  bucket = "dummy-bucket"
  source = "path/to/function.zip"
}

resource "google_cloudfunctions_function" "function" { 
  name        = var.function_name
  project     = var.project_id
  region      = var.location
  runtime     = "python310"
  entry_point = "handler" #llamada al codigo de la funcion

  source_archive_bucket = "dummy-bucket"
  source_archive_object = "dummy-object.zip"

  trigger_http = true

  available_memory_mb   = 128
  timeout               = 60

  ingress_settings = "ALLOW_ALL"
}

resource "google_pubsub_subscription" "subs" {
  for_each = google_pubsub_topic.topics

  name  = "${each.value.name}-push-sub"
  topic = each.value.name
  project = var.project_id

  push_config {
    push_endpoint = google_cloudfunctions_function.function.https_trigger_url
  }

  ack_deadline_seconds = 10
}
