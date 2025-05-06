resource "google_pubsub_topic" "topic" {
  name = var.topic_name
}

resource "google_pubsub_subscription" "subscription" {
  name  = var.subscription_name
  topic = google_pubsub_topic.topic.id

  ack_deadline_seconds = 10

  labels = var.subscription_labels

  dynamic "push_config" {
    for_each = var.push_endpoint != null ? [1] : []
    content {
      push_endpoint = var.push_endpoint

      attributes = {
        x-goog-version = "v1"
      }
    }
  }
}
