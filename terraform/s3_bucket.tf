resource "aws_s3_bucket" "article_storage" {
  bucket = "c22-dashboard-divas-article-storage"

  tags = {
    Project     = "MediaOutlets"
    Environment = "dev"
    ManagedBy   = "Terraform"
    TeamName    = "DashboardDivas"
  }
}

resource "aws_s3_bucket_versioning" "article_storage_versioning" {
  bucket = aws_s3_bucket.article_storage.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_public_access_block" "article_storage_public_access" {
  bucket = aws_s3_bucket.article_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}