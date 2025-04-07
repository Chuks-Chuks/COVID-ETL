output "rds_connection_details" {
  description = "RDS instance connection details"
  value = {
    endpoint = aws_db_instance.covid_db.endpoint
    username = aws_db_instance.covid_db.username
    port     = aws_db_instance.covid_db.port
    database = "postgres"  # Default database
  }
  sensitive = true  # Hides values in console output
}

output "rds_instance_id" {
  description = "RDS instance identifier"
  value       = aws_db_instance.covid_db.id
}