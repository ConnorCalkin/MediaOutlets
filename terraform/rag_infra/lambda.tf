resource "aws_iam_role" "lambda_execution" {
    name = "c22-dashboard-divas-rag-lambda-role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "lambda.amazonaws.com"
            }
        }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
    role       = aws_iam_role.lambda_execution.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "rag" {
    function_name = "c22-dashboard-divas-rag"
    role          = aws_iam_role.lambda_execution.arn
    package_type  = "Image"

    image_uri = var.image_uri

    timeout = 30

    environment {
        variables = {
        CHROMA_HOST    = var.chroma_host
        CHROMA_PORT    = var.chroma_port
        OPENAI_API_KEY = var.openai_api_key
        }
    }
}