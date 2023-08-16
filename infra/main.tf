provider "aws" {
    region = "us-west-2" # Replace with your desired region
}

resource "aws_lambda_function" "example" {
    function_name    = "example-lambda"
    role             = aws_iam_role.lambda.arn
    handler          = "app.lambda_handler"
    runtime          = "python3.8"
    filename         = "example_lambda.zip"
    source_code_hash = filebase64sha256("example_lambda.zip")
}

resource "aws_iam_role" "lambda" {
    name = "example-lambda-role"

    assume_role_policy = jsonencode({
        Version   = "2012-10-17"
        Statement = [
            {
                Action    = "sts:AssumeRole"
                Effect    = "Allow"
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda" {
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    role       = aws_iam_role.lambda.name
}

data "archive_file" "lambda" {
    type        = "zip"
    source_dir  = "${path.module}/app"
    output_path = "${path.module}/example_lambda.zip"
}

resource "null_resource" "lambda_zip" {
    triggers = {
        always_run = timestamp()
    }

    provisioner "local-exec" {
        command = "cd ${path.module} && zip -r example_lambda.zip app"
    }
}

resource "aws_api_gateway_rest_api" "example" {
    name        = "example-api"
    description = "Example API"
}

resource "aws_api_gateway_resource" "example" {
    rest_api_id = aws_api_gateway_rest_api.example.id
    parent_id   = aws_api_gateway_rest_api.example.root_resource_id
    path_part   = "example"
}

resource "aws_api_gateway_method" "example" {
    rest_api_id   = aws_api_gateway_rest_api.example.id
    resource_id   = aws_api_gateway_resource.example.id
    http_method   = "POST"
    authorization = "NONE"
}

resource "aws_api_gateway_integration" "example" {
    rest_api_id             = aws_api_gateway_rest_api.example.id
    resource_id             = aws_api_gateway_resource.example.id
    http_method             = aws_api_gateway_method.example.http_method
    integration_http_method = "POST"
    type                    = "AWS_PROXY"
    uri                     = aws_lambda_function.example.invoke_arn
}

resource "aws_api_gateway_deployment" "example" {
    rest_api_id = aws_api_gateway_rest_api.example.id
    stage_name  = "prod"
}

