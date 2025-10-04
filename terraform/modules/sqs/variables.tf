# SQS Module Variables

variable "queue_name" {
  description = "Name of the main SQS queue"
  type        = string
}

variable "dlq_name" {
  description = "Name of the Dead Letter Queue"
  type        = string
}

variable "visibility_timeout" {
  description = "SQS visibility timeout in seconds"
  type        = number
  default     = 600
}

variable "max_receive_count" {
  description = "Maximum number of times a message can be received before moving to DLQ"
  type        = number
  default     = 3
}

variable "message_retention_days" {
  description = "Number of days to retain messages in the queue"
  type        = number
  default     = 14
}

variable "tags" {
  description = "Tags to apply to SQS resources"
  type        = map(string)
  default     = {}
}
