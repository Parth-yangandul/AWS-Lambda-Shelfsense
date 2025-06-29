# Output the API Gateway Invoke URL
output "api_invoke_url" {
  description = "Base URL to invoke the ShelfSense API"
  value       = "https://${aws_api_gateway_rest_api.shelf_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.dev.stage_name}"
}

# Output Lambda ARNs
output "add_item_lambda_arn" {
  description = "ARN for Add Item Lambda"
  value       = aws_lambda_function.add_item_lambda.arn
}

output "get_items_lambda_arn" {
  description = "ARN for Get Items Lambda"
  value       = aws_lambda_function.get_items_lambda.arn
}

output "update_item_lambda_arn" {
  description = "ARN for Update Item Lambda"
  value       = aws_lambda_function.update_item_lambda.arn
}

output "check_expiry_lambda_arn" {
  description = "ARN for Check Expiry Lambda"
  value       = aws_lambda_function.check_expiry_lambda.arn
}

# Output SNS Topic
output "sns_topic_arn" {
  description = "SNS Topic ARN for alerts"
  value       = aws_sns_topic.expiry_alerts.arn
}