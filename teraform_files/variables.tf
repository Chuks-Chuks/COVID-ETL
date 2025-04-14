variable "db_password" {
  description = "RDS PostgreSQL password"
  type        = string
  sensitive   = true  # Hides value in logs
}

variable "db_username" {
  description = "RDS Username"
  type = string
  sensitive = true
}