resource "google_pubsub_topic" "default" {
  name = "chatbot-topic"
}

resource "google_storage_bucket" "default" {
  name                        = var.bucket_pubsub_name
  location                    = var.region
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "default" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.default.name
  source = "${path.module}/index.zip"
}

resource "google_cloudfunctions2_function" "default" {
  name        = "function"
  location    = var.region
  description = "a new function"

  build_config {
    runtime     = "python310"
    entry_point = "process_pubsub_message"
    environment_variables = {
      BUILD_CONFIG_TEST = "build_test"
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.default.name
      }
    }
  }

  service_config {
    available_memory   = "512M"
    timeout_seconds    = 60
    environment_variables = {
      SERVICE_CONFIG_TEST = "config_test"
    }
    ingress_settings               = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email          = google_service_account.default.email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.default.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_pubsub_topic.default,
  ]
}