provider "aws" {
  region = var.aws_region
}

# DynamoDB Table
resource "aws_dynamodb_table" "food_items" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "item_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "item_id"
    type = "S"
  }

  tags = {
    Name        = "FoodItemsTable"
    Environment = "dev"
  }
}

# IAM Role and Policies
resource "aws_iam_role" "lambda_exec_role" {
  name = var.lambda_exec_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = var.lambda_basic_policy_name
  description = "Lambda policy for ShelfSense basic operations"
  policy      = data.aws_iam_policy_document.lambda_policy_doc.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:Scan",
      "dynamodb:Query"
    ]
    resources = ["*"]
    effect    = "Allow"
  }
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_policy" "lambda_sns_policy" {
  name   = var.lambda_sns_policy_name
  policy = data.aws_iam_policy_document.lambda_sns_doc.json
}

data "aws_iam_policy_document" "lambda_sns_doc" {
  statement {
    effect = "Allow"
    actions = [
      "logs:*",
      "dynamodb:*",
      "sns:Publish"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_sns_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_sns_policy.arn
}

# Lambda Functions
resource "aws_lambda_function" "add_item_lambda" {
  function_name    = "add_item_lambda"
  handler          = "add_item_lambda.lambda_handler"
  runtime          = "python3.9"
  filename         = var.lambda_add_zip
  source_code_hash = filebase64sha256(var.lambda_add_zip)
  role             = aws_iam_role.lambda_exec_role.arn
}

resource "aws_lambda_function" "get_items_lambda" {
  function_name    = "get_items_lambda"
  filename         = var.lambda_get_zip
  handler          = "get_items_lambda.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.food_items.name
    }
  }
}

resource "aws_lambda_function" "update_item_lambda" {
  function_name    = "update_item_lambda"
  filename         = var.lambda_update_zip
  handler          = "update_item_lambda.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.food_items.name
    }
  }
}

resource "aws_lambda_function" "check_expiry_lambda" {
  function_name    = "check_expiry_lambda"
  handler          = "check_expiry_lambda.lambda_handler"
  runtime          = "python3.9"
  filename         = var.lambda_check_zip
  source_code_hash = filebase64sha256(var.lambda_check_zip)
  role             = aws_iam_role.lambda_exec_role.arn
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.expiry_alerts.arn
    }
  }
}

# SNS Topic and Subscription
resource "aws_sns_topic" "expiry_alerts" {
  name = var.sns_topic_name
}

resource "aws_sns_topic_subscription" "alert_sms" {
  topic_arn = aws_sns_topic.expiry_alerts.arn
  protocol  = "sms"
  endpoint  = var.alert_sms_endpoint
}

# CloudWatch Events
resource "aws_cloudwatch_event_rule" "daily_expiry_check" {
  name                = "daily-expiry-check"
  description         = "Triggers check_expiry_lambda every day at 8:30 AM IST"
  schedule_expression = var.expiry_schedule_cron
}

resource "aws_cloudwatch_event_target" "invoke_check_expiry_lambda" {
  rule      = aws_cloudwatch_event_rule.daily_expiry_check.name
  target_id = "CheckExpiryLambdaTarget"
  arn       = aws_lambda_function.check_expiry_lambda.arn
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.check_expiry_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_expiry_check.arn
}

# API Gateway & Resources
resource "aws_api_gateway_rest_api" "shelf_api" {
  name        = var.api_name
  description = var.api_description
}

resource "aws_api_gateway_resource" "add_item_resource" {
  rest_api_id = aws_api_gateway_rest_api.shelf_api.id
  parent_id   = aws_api_gateway_rest_api.shelf_api.root_resource_id
  path_part   = "add-item"
}

resource "aws_api_gateway_method" "post_method" {
  rest_api_id   = aws_api_gateway_rest_api.shelf_api.id
  resource_id   = aws_api_gateway_resource.add_item_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.shelf_api.id
  resource_id             = aws_api_gateway_resource.add_item_resource.id
  http_method             = aws_api_gateway_method.post_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.add_item_lambda.invoke_arn
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.add_item_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.shelf_api.execution_arn}/*/*"
}

resource "aws_api_gateway_resource" "get_items_resource" {
  rest_api_id = aws_api_gateway_rest_api.shelf_api.id
  parent_id   = aws_api_gateway_rest_api.shelf_api.root_resource_id
  path_part   = "get-items"
}

resource "aws_api_gateway_method" "get_items_method" {
  rest_api_id   = aws_api_gateway_rest_api.shelf_api.id
  resource_id   = aws_api_gateway_resource.get_items_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_items_integration" {
  rest_api_id             = aws_api_gateway_rest_api.shelf_api.id
  resource_id             = aws_api_gateway_resource.get_items_resource.id
  http_method             = aws_api_gateway_method.get_items_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_items_lambda.invoke_arn
}

resource "aws_lambda_permission" "apigw_get_items" {
  statement_id  = "AllowAPIGatewayInvokeGetItems"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_items_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.shelf_api.execution_arn}/*/*"
}

resource "aws_api_gateway_resource" "update_item" {
  rest_api_id = aws_api_gateway_rest_api.shelf_api.id
  parent_id   = aws_api_gateway_rest_api.shelf_api.root_resource_id
  path_part   = "update-item"
}

resource "aws_api_gateway_method" "post_update_item" {
  rest_api_id   = aws_api_gateway_rest_api.shelf_api.id
  resource_id   = aws_api_gateway_resource.update_item.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "update_item_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.shelf_api.id
  resource_id             = aws_api_gateway_resource.update_item.id
  http_method             = aws_api_gateway_method.post_update_item.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_item_lambda.invoke_arn
}

resource "aws_lambda_permission" "apigw_update_item" {
  statement_id  = "AllowAPIGatewayInvokeUpdateItem"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_item_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.shelf_api.execution_arn}/*/POST/update-item"
}

resource "aws_api_gateway_deployment" "shelf_api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.shelf_api.id
  triggers = {
    redeploy = timestamp()
  }
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_integration.get_items_integration,
    aws_api_gateway_integration.update_item_lambda
  ]
}

resource "aws_api_gateway_stage" "dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.shelf_api.id
  deployment_id = aws_api_gateway_deployment.shelf_api_deployment.id
}
