# Variables for Aquifer Simulation Infrastructure

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "aquifer-test-simulation"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 600
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 2048
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 1
}

variable "sqs_visibility_timeout" {
  description = "SQS visibility timeout in seconds"
  type        = number
  default     = 600
}

variable "sqs_max_receive_count" {
  description = "Maximum number of times a message can be received before moving to DLQ"
  type        = number
  default     = 3
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
