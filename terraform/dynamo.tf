resource "aws_dynamodb_table" "articles" {
  name         = "c22-dashboard-divas-db"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  tags = {
    Project     = "MediaOutlets"
    Environment = "dev"
    ManagedBy   = "Terraform"
    TeamName    = "DashboardDivas"
  }
}