# =============================
# variables.tf
# =============================

variable "region" {
  description = "AWS region"
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix"
  default     = "ShelfSense"
}

variable "sns_alert_email" {
  description = "Email endpoint for SNS alerts"
  type        = string
  default     = ""
}

variable "sns_alert_sms" {
  description = "Phone number for SNS alerts (with country code)"
  type        = string
  default     = "+918530731105"
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name"
  default     = "FoodItems"
}

variable "add_lambda_zip" {
  default = "../lambda/add_item_lambda.zip"
}

variable "get_lambda_zip" {
  default = "../lambda/get_items_lambda.zip"
}

variable "update_lambda_zip" {
  default = "../lambda/update_item_lambda.zip"
}

variable "check_lambda_zip" {
  default = "../lambda/check_expiry_lambda.zip"
}
