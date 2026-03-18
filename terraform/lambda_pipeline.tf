
#access the ECR repository for pipeline docker image
data "aws_ecr_repository" "rss_pipeline" {
     name = "c22-dashboard-divas-rss-pipeline"
}

# IAM role (Identity the lambda function will assume when executing)
resource "aws_iam_role" "lambda_execution_role" {
  name = "c22-dashboard-divas-pipeline-lambda-role"

  assume_role_policy =  jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
      }
    ]
  })    
}   

#IAM Policy - the permissions
resource "aws_iam_policy" "lambda_permissions"{
    name = "c22-dashboard-divas-pipeline-lambda-permissions"
    
    policy = jsonencode({
        "Version": "2012-10-17",
        "Statement" = [
        #Allow the Lambda function to interact with DynamoDB
      {
        "Effect"   = "Allow"
        "Action"   = ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem"]
        "Resource" = "arn:aws:dynamodb:*:*:table/rss_data_table" 
      },
        #Allow the Lambda function to interact with S3 
      {
        "Effect"   = "Allow"
        "Action"   = ["s3:PutObject", "s3:ListBucket"]
        "Resource" = ["arn:aws:s3:::your-bucket-name", "arn:aws:s3:::your-bucket-name/*"]
      },
        #Allow the Lambda function to write logs to CloudWatch
      {
        "Effect"   = "Allow"
        "Action"   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        "Resource" = "arn:aws:logs:*:*:*"
      }
    ]
    })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_permissions.arn
}   

# 4. The Lambda Function
resource "aws_lambda_function" "rss_pipeline_lambda" {
  function_name = "rss-pipeline-service"
  role          = aws_iam_role.lambda_execution_role.arn
  package_type  = "Image"
  
  # Using the data block to get the URI
  image_uri     = "${data.aws_ecr_repository.rss_pipeline.repository_url}:latest"

  # Defaults: 128MB memory and 3s timeout
  memory_size = 256
  timeout     = 300

  environment {
    variables = {
      OPENAI_API_KEY = var.OPENAI_API_KEY
    } 
  }
}

# EventBridge: The Scheduler : runs every 6 hours catches major news cycles like morning, afternoon, evening, and late night. 
# balances frequency with cost ensuring timely updates without too much unnecessary costs.
resource "aws_cloudwatch_event_rule" "every_six_hours" {
  name                = "rss-pipeline-schedule"
  description         = "Triggers the RSS scraper every 6 hours"
  schedule_expression = "rate(6 hours)"
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  rule      = aws_cloudwatch_event_rule.every_six_hours.name
  target_id = "rss_pipeline_target"
  arn       = aws_lambda_function.rss_pipeline_lambda.arn
}

# Permission for EventBridge to call Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rss_pipeline_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_six_hours.arn
}