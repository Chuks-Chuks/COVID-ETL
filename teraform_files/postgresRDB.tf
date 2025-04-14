resource "aws_db_instance" "covid_db" {
  identifier             = "covid-postgres"
  allocated_storage      = 15            # GB (Free Tier: 20 GB)
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "15.10"
  instance_class         = "db.t3.micro" # Free Tier eligible
  username               = var.db_username
  password               = var.db_password 
  publicly_accessible    = true          
  skip_final_snapshot    = true          
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

resource "aws_security_group" "rds_sg" {
  name = "rds_sg"
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow all IPs (not recommended for production)
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}