provider "aws" {
  region = "us-east-1"
}

resource "aws_ecr_repository" "repo" {
  name = "s3-to-rds-glue-pipe"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "rablo-bucket-pipe-2804"
}

resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "myname-rds-group-devops-1"
  subnet_ids = [
    "subnet-0cfad3abff5b7bbac", # rablo-subnet-1
    "subnet-0c396d12e6587eec0"  # rablo-subnet-2
  ]
  description = "RDS subnet group for Rablo PostgreSQL DB"
}

resource "aws_db_instance" "rds" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "17.6"
  instance_class       = "db.t3.micro"
  username             = "Rablodbuser"
  password             = "Granadeaa12"
  parameter_group_name = "default.postgres17"
  skip_final_snapshot  = true
 
  # Reference the DB subnet group here
  db_subnet_group_name = aws_db_subnet_group.rds_subnet_group.name
}
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-exec-role-pipe1"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_policy" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "my_lambda" {
  function_name = "s3_to_rds_glue_lambda-pipe1"
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.repo.repository_url}:latest"
  role          = aws_iam_role.lambda_exec_role.arn
  timeout       = 60
}
