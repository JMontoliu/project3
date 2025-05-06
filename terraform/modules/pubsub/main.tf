resource "google_pubsub_topic" "topics" {
  for_each = toset(var.topics)

  name    = each.value
  project = var.project_id
}
