# SQS Module - Creates SQS queue with Dead Letter Queue

# SQS Main Queue
resource "aws_sqs_queue" "main_queue" {
  name                      = var.queue_name
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = var.message_retention_days * 24 * 60 * 60  # Convert days to seconds
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = var.visibility_timeout

  tags = var.tags
}

# SQS Dead Letter Queue
resource "aws_sqs_queue" "dlq" {
  name                      = var.dlq_name
  message_retention_seconds = var.message_retention_days * 24 * 60 * 60  # Convert days to seconds

  tags = var.tags
}

# SQS Queue Redrive Policy
resource "aws_sqs_queue_redrive_policy" "main_queue" {
  queue_url = aws_sqs_queue.main_queue.id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}
