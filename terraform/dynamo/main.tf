provider "aws" {
  region = "eu-west-2"
}

resource "aws_dynamodb_table" "articles" {
  name         = "c22-dashboard-divas-db"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "article_url"
  range_key    = "published_date"

  attribute {
    name = "article_url"
    type = "S"
  }

  attribute {
    name = "published_date"
    type = "S"
  }

  tags = {
    Project     = "MediaOutlets"
    Environment = "dev"
    ManagedBy   = "Terraform"
    TeamName    = "DashboardDivas"
  }
}