resource "aws_apigatewayv2_api" "rag_api" {
    name          = "c22-dashboard-divas-rag-api"
    protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "rag_lambda" {
    api_id                 = aws_apigatewayv2_api.rag_api.id
    integration_type       = "AWS_PROXY"
    integration_uri        = aws_lambda_function.rag.invoke_arn
    payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "query" {
    api_id    = aws_apigatewayv2_api.rag_api.id
    route_key = "POST /query"
    target    = "integrations/${aws_apigatewayv2_integration.rag_lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
    api_id      = aws_apigatewayv2_api.rag_api.id
    name        = "$default"
    auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
    statement_id  = "AllowAPIGatewayInvoke"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.rag.function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "${aws_apigatewayv2_api.rag_api.execution_arn}/*/*"
}