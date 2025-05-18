output "sql_host" {
    description = "SQL Public IP"
    value = google_sql_database_instance.postgres.ip_address[0].ip_address
}