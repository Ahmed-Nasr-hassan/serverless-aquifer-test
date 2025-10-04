# SQS Module Outputs

output "queue_url" {
  description = "URL of the main SQS queue"
  value       = aws_sqs_queue.main_queue.url
}

output "queue_arn" {
  description = "ARN of the main SQS queue"
  value       = aws_sqs_queue.main_queue.arn
}

output "queue_name" {
  description = "Name of the main SQS queue"
  value       = aws_sqs_queue.main_queue.name
}

output "dlq_url" {
  description = "URL of the Dead Letter Queue"
  value       = aws_sqs_queue.dlq.url
}

output "dlq_arn" {
  description = "ARN of the Dead Letter Queue"
  value       = aws_sqs_queue.dlq.arn
}

output "dlq_name" {
  description = "Name of the Dead Letter Queue"
  value       = aws_sqs_queue.dlq.name
}
